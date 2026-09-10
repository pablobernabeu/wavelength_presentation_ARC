#!/bin/bash
# Copied unmodified from the speech-transcription workflow, except that two directory
# names have been replaced with <project> and <project-env>. That project is not public,
# and no filesystem path from it appears in this repository.
# =============================================================================
# submit_sweep.sh  —  Full cross-suite × cross-condition WER benchmark sweep
#
# Submits a SLURM array job where each task runs one suite against all
# selected conditions for a single ASR model, using
# evaluation/sweep.py.  Conditions are scored in a single audio pass per
# suite, so adding conditions costs no extra transcription time.
#
# Suite indices (--array=0-4):
#
#   0  librispeech_clean    librispeech_asr clean/test           ~2,620 utts
#   1  ami                  edinburghcstr/ami ihm/test           ~12,600 utts
#   2  fleurs               google/fleurs en_us/test             ~   400 utts
#   3  librispeech_other    librispeech_asr other/test           ~2,939 utts
#   4  voxpopuli_accented   facebook/voxpopuli en_accented/test  ~9,000 utts
#
# (Indices 1-4 follow the alphabetical order used by evaluation/sweep.py,
# which calls challenge_suites.list_suites() — sorted by name.  Check
# the current index table with:
#   python -m evaluation.sweep --list-suites)
#
# Default conditions per suite:
#
#   librispeech_clean:  raw, repetition_fix, filler_strip, dedup_window,
#                       punct_strip, case_fold, whisper_norm
#   challenge suites:   raw, filler_strip, dedup_window,
#                       punct_strip, case_fold, whisper_norm
#
# Override examples (set before sbatch):
#
#   SWEEP_MODEL=openai/whisper-medium       sbatch hpc/submit_sweep.sh
#   SWEEP_CONDITIONS=raw,whisper_norm       sbatch hpc/submit_sweep.sh
#   SWEEP_LIMIT=500                         sbatch hpc/submit_sweep.sh
#   sbatch --array=0     hpc/submit_sweep.sh   # LibriSpeech only
#   sbatch --array=1-4   hpc/submit_sweep.sh   # challenge suites only
#   sbatch --array=2     hpc/submit_sweep.sh   # voxpopuli only
#
# Outputs are written to:
#   $DATA/<project-env>/output/evaluation/
#
# After all tasks complete, run the aggregation job:
#   sbatch hpc/aggregate_sweep.sh
#
# Or aggregate with dependency on this job:
#   JID=$(sbatch --parsable hpc/submit_sweep.sh)
#   sbatch --dependency=afterok:${JID} hpc/aggregate_sweep.sh
#
# Usage (submit from the repository root on ARC):
#   sbatch hpc/submit_sweep.sh
# =============================================================================

#SBATCH --job-name=wer_sweep
#SBATCH --array=0-4
#SBATCH --partition=short
#SBATCH --clusters=htc
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --output=logs/wer_sweep_%A_%a.out
#SBATCH --error=logs/wer_sweep_%A_%a.err

set -euo pipefail

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
module purge
module load Anaconda3 || true
module load CUDA     || true

REPO_DIR="${SLURM_SUBMIT_DIR:-$HOME/<project>}"                 # redacted, see header
ACTIVATION_SCRIPT="$REPO_DIR/activate_project_env_arc.sh"
if [[ -f "$ACTIVATION_SCRIPT" ]]; then
    # shellcheck source=/dev/null
    source "$ACTIVATION_SCRIPT"
else
    echo "❌ Activation script not found at $ACTIVATION_SCRIPT" >&2
    exit 1
fi

cd "$REPO_DIR"
unset TRANSFORMERS_CACHE

echo "GPU: ${CUDA_VISIBLE_DEVICES:-not set by SLURM}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || true

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------
python -c "import datasets" 2>/dev/null \
    || pip install --quiet "datasets>=2.14.0"

if ! python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    echo "PyTorch CUDA not available — reinstalling with CUDA 12.1 wheels..." >&2
    pip uninstall -y torch torchvision torchaudio 2>&1 | tail -n 5 || true
    pip install --force-reinstall --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cu121
fi
python -c "import torch; print('CUDA available:', torch.cuda.is_available(), \
    '| device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'n/a', \
    '| torch:', torch.__version__)"
python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)" || {
    echo "❌ CUDA still unavailable after reinstall; aborting." >&2
    exit 2
}

# ---------------------------------------------------------------------------
# Sweep parameters
# ---------------------------------------------------------------------------
REPORT_DIR="${DATA}/<project-env>/output/evaluation"            # redacted, see header
mkdir -p "$REPORT_DIR" logs

MODEL="${SWEEP_MODEL:-openai/whisper-large-v3}"

# An explicit SWEEP_CONDITIONS value overrides the per-suite defaults
# baked into evaluation/sweep.py.  Leave unset to use those defaults.
CONDITIONS_ARG=()
if [[ -n "${SWEEP_CONDITIONS:-}" ]]; then
    CONDITIONS_ARG=(--conditions "$SWEEP_CONDITIONS")
fi

LIMIT_ARG=()
if [[ -n "${SWEEP_LIMIT:-}" ]]; then
    LIMIT_ARG=(--limit "$SWEEP_LIMIT")
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  WER sweep  |  array task ${SLURM_ARRAY_TASK_ID}  |  model: ${MODEL}"
echo "  Output dir: ${REPORT_DIR}"
echo "  Started:    $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python -m evaluation.sweep \
    --suite-index "${SLURM_ARRAY_TASK_ID}" \
    --model       "${MODEL}"               \
    --output-dir  "${REPORT_DIR}"          \
    --seed        42                       \
    "${CONDITIONS_ARG[@]}"                 \
    "${LIMIT_ARG[@]}"

echo ""
echo "✅ Task ${SLURM_ARRAY_TASK_ID} complete at $(date)"
echo "   Outputs: ${REPORT_DIR}"
