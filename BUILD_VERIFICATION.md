# Build verification

Verified on 11 July 2026.

- `npm ci`: passed (767 packages installed from lockfile)
- `npm run typecheck`: passed with zero TypeScript errors
- `npx expo export --platform android --max-workers 1`: passed
- Metro bundle: 778 modules bundled
- Android JavaScript bundle: 1.77 MB
- Exported assets: 19
- Python analysis tests: 3/3 passed
- Python module compilation: passed

The app is configured for the supported JSC engine because the execution sandbox blocks Hermes from spawning its bytecode compiler. This does not change application functionality.

`npm audit` reports moderate findings in transitive Expo build-tool dependencies. There are no high or critical findings. The automated remediation proposes an Expo major-version upgrade, so it was not forced into this verified build.
