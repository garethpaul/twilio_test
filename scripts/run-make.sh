#!/bin/sh
set -eu

case $0 in
  /*) SCRIPT_PATH=$0 ;;
  *) SCRIPT_PATH=$(/bin/pwd -P)/$0 ;;
esac

LINK_COUNT=0
while [ -L "$SCRIPT_PATH" ]; do
  LINK_COUNT=$((LINK_COUNT + 1))
  if [ "$LINK_COUNT" -gt 40 ]; then
    printf '%s\n' 'repository verification entrypoint has too many symbolic links' >&2
    exit 66
  fi

  if ! LINK_TARGET_WITH_SENTINEL=$(/usr/bin/readlink -n "$SCRIPT_PATH" && printf x); then
    printf '%s\n' 'repository verification entrypoint could not read symbolic link' >&2
    exit 66
  fi
  LINK_TARGET=${LINK_TARGET_WITH_SENTINEL%x}
  case $LINK_TARGET in
    /*) SCRIPT_PATH=$LINK_TARGET ;;
    *) SCRIPT_PATH=$(/usr/bin/dirname "$SCRIPT_PATH")/$LINK_TARGET ;;
  esac
done

if [ ! -f "$SCRIPT_PATH" ]; then
  printf '%s\n' 'repository verification entrypoint did not resolve to a regular file' >&2
  exit 66
fi

SCRIPT_DIR=$(CDPATH='' cd -P "$(/usr/bin/dirname "$SCRIPT_PATH")" && /bin/pwd -P)
ROOT_DIR=$(CDPATH='' cd -P "$SCRIPT_DIR/.." && /bin/pwd -P)

if [ "$#" -ne 1 ]; then
  printf '%s\n' 'usage: scripts/run-make.sh check|lint' >&2
  exit 64
fi

case $1 in
  check|lint) TARGET=$1 ;;
  *)
    printf 'unsupported repository verification target: %s\n' "$1" >&2
    exit 64
    ;;
esac

exec /usr/bin/env -u MAKEFILES -u MAKEFLAGS -u MFLAGS -u MAKEOVERRIDES -u GNUMAKEFLAGS /usr/bin/make --no-print-directory -f "$ROOT_DIR/Makefile" "$TARGET"
