# Contributing to Video Shotcraft

Thank you for your interest in **Video Shotcraft**, the open-source cinematic shot recipe cards and 2.5D camera animation toolkit for AI coding agents.

## How to Contribute

1. **Add New Shot Recipe Cards**:
   - New shot cards should be documented under `references/shots/<category>/` with clear duration, Remotion animation recipes, camera trajectories, and sound design recommendations.
2. **Improve Remotion Templates**:
   - Enhance templates in `template/` to support more camera movements, easing curves, and UI components.
3. **Pull Request Guidelines**:
   - Fork the repository and create a descriptive branch: `git checkout -b feature/new-shot-card`.
   - Ensure the template builds cleanly: `npm run build` or `npm test`.
   - Open a PR with visual demo previews or GIFs if possible.
