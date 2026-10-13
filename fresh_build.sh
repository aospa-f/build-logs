#!/usr/bin/env bash
#
# fresh_build.sh
# Convenience wrapper for scripts/fresh_server_build.sh
#
exec bash "$(dirname "$0")/scripts/fresh_server_build.sh" "$@"
