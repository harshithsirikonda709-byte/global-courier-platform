import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  webpack: (config) => {
    const oneOfRule = config.module?.rules?.find(
      (rule: { oneOf?: unknown[] }) => Array.isArray(rule?.oneOf)
    );
    if (oneOfRule && Array.isArray(oneOfRule.oneOf)) {
      for (const rule of oneOfRule.oneOf) {
        if (
          rule?.use &&
          Array.isArray(rule.use) &&
          rule.use.some(
            (u: { loader?: string }) =>
              typeof u?.loader === "string" && u.loader.includes("css-loader")
          )
        ) {
          rule.use.push("@tailwindcss/turbopack");
        }
      }
    }
    return config;
  },
};

export default nextConfig;
