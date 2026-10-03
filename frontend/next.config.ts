import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // self-contained build so the Docker image stays small (see Dockerfile)
  output: "standalone",
};

export default nextConfig;
