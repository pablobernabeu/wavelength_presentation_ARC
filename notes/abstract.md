# Abstract

**On the same wavelength: Words, brainwaves and HPC**
Pablo Bernabeu · Department of Education, University of Oxford
Oxford Research Computing Community Event, 10 September 2026

---

Psycholinguistic analysis has moved onto the cluster, largely because of what we now do with
the data. We model individual trials instead of condition averages, we simulate whole study
designs before recruiting anyone, and we transcribe interviews that cannot leave the
institution.

This talk describes three strands of my work on ARC. The first is large behavioural datasets,
where the number of participants a study needs has no closed formula and must be estimated by
simulation. The second is EEG, where keeping every trial turns an analysis that once ran on a
laptop into a week of computation. The third is speech, where data protection rules out cloud
transcription and where a GPU earns its place.

I will be specific about where the machine learning and the GPU work sit, because the
distribution may be unexpected. Two of the three strands run entirely on CPUs, and the longest
job I will describe is a machine-learning analysis that never requests a GPU.

I will also say what went wrong, how a scheduler setting came to fix the replicate count in a
published table, and what would help me most from ARC. The binding constraint is seldom raw
speed. More often it is memory, a toolchain or a wall-clock limit.

---

*209 words.*
