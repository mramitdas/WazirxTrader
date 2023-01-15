if [ "$VIRTUAL_ENV" == "" ]; then
    ABS_ENV_DIR=$(cd ${1:-../env} && pwd -P)
    ACTIVATE_SCRIPT="$ABS_ENV_DIR/bin/activate"
    if [ -f "$ACTIVATE_SCRIPT" ]; then
        echo "Env: Activated"
        . $ACTIVATE_SCRIPT
    else
        echo "Env: Not found"
    fi
else
    echo "Env: Already activated"
fi
