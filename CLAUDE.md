# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a frontend application project (AI-front-test) designed for network session analysis with ClickHouse database integration. The project requirements include:

1. Auto-generated frontend pages
2. Simple login interface with post-login statistics viewing
3. User management interface (add, delete, modify users)
4. ClickHouse integration for basic five-tuple session statistics
5. Multi-dimensional query display by session, IP, and other dimensions

## Current State

The repository currently contains only basic documentation (README.md). The codebase structure, build tools, and development setup have not yet been implemented.

## Development Setup

Since this is a fresh project without existing configuration:
- No package.json or build scripts are currently configured
- No frontend framework has been selected yet
- No development server or build tools are set up
- No testing framework is configured

## Architecture Notes

The application will need to implement:
- Frontend framework selection (React, Vue, or similar)
- Authentication system for login functionality
- User management CRUD operations
- ClickHouse database connectivity for session data
- Multi-dimensional data filtering and visualization components

## Next Steps for Development

When implementing this project, consider:
- Choose appropriate frontend framework and tooling
- Set up build configuration (webpack, vite, or framework defaults)
- Configure development and production environments
- Implement ClickHouse client integration
- Design responsive UI for statistics dashboard