# Versioned configuration

Add small public dataset manifests under `datasets/` and validated routing
inventories, policies, price catalogues and context strategies under `routing/`
as VS1 preflight establishes them. Retain versions referenced by completed runs.
The research pack's routing YAML is a source recommendation, not active config.

Never commit credentials, machine-specific absolute paths, private manifests or
full datasets. Use an ignored `.env` or local profile for workstation settings;
`.env.example` lists intended settings without claiming an implemented loader.
