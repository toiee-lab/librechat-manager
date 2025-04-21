# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands
- Build: `npm run frontend` or `bun run b:client` 
- Development: `npm run frontend:dev` or `bun run b:client:dev`
- Server: `npm run backend` or `bun run b:api`
- Lint: `npm run lint` (fix with `npm run lint:fix`)
- Format: `npm run format`
- Tests: 
  - All: `npm run test`
  - API: `npm run test:api`
  - Client: `npm run test:client`
  - Single test: `cd api && npx jest path/to/test.js` or `cd client && npx jest path/to/test.tsx`

## Code Style Guidelines
- Indentation: 2 spaces
- Line length: 120 characters max
- Quotes: Single quotes
- Semicolons: Required
- TypeScript: Strict mode enabled
- Import paths: Use aliases (`~/*` for client src, `librechat-data-provider/*` for data provider)
- Error handling: Use try/catch blocks with appropriate error logging
- React: Follow hooks rules, use functional components
- Avoid prop drilling, prefer context where appropriate
- Use type annotations for function parameters and return values