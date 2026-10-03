# TEI publishes separate per-arch CPU images (no multi-arch tag), so pick one
# from the build platform: amd64 on Linux servers, arm64 on Apple Silicon.
ARG TEI_VERSION=1.9
FROM ghcr.io/huggingface/text-embeddings-inference:cpu-${TEI_VERSION} AS tei-amd64
FROM ghcr.io/huggingface/text-embeddings-inference:cpu-arm64-${TEI_VERSION} AS tei-arm64
FROM tei-${TARGETARCH}
