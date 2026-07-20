import type { Plugin } from "@opencode-ai/plugin";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

export default (async () => {
  return {
    config: async (cfg) => {
      if (!cfg.provider) cfg.provider = {};

      const hideProviders = ["openai", "deepseek", "cloudflare", "opencode"];
      for (const hp of hideProviders) {
        if (!cfg.provider[hp]) cfg.provider[hp] = {};
        cfg.provider[hp].models = {};
      }
      
      if (!cfg.provider["vertex"]) cfg.provider["vertex"] = {};
      cfg.provider["vertex"].models = {};

      const CACHE_PATH = path.join(os.homedir(), ".config/opencode/models-cache.json");
      
      try {
        if (fs.existsSync(CACHE_PATH)) {
          const raw = fs.readFileSync(CACHE_PATH, "utf8");
          const cachedProviders = JSON.parse(raw);
          
          for (const [providerId, modelsArray] of Object.entries(cachedProviders)) {
            if (!cfg.provider[providerId]) cfg.provider[providerId] = {};
            const pCfg = cfg.provider[providerId];
            if (!pCfg.models) pCfg.models = {};
            
            for (const model of (modelsArray as any[])) {
              if (model.name && !pCfg.models[model.name]) {
                pCfg.models[model.name] = model;
              }
            }
          }
        }
      } catch (e) {
        // Silently proceed if cache fails to read
      }
    }
  };
}) satisfies Plugin;
