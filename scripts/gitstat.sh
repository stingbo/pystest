#!/bin/bash
#-------------------------------------------------------
set -x
set -e

OUT_ROOT=/opt/deploy/gitstat

COMMIT_DATE=`date "+%y%m%d"`

DIFF_DIR=$OUT_ROOT/$CI_PROJECT_NAMESPACE/$CI_PROJECT_NAME/$COMMIT_DATE/${CI_BUILD_REF_NAME}/$CI_COMMIT_SHA

DIFF_FILE=$DIFF_DIR/diff
LOG_FILE=$DIFF_DIR/log
DIFF_CMD_FILE=$DIFF_DIR/log.diff.sh


[ -d $DIFF_DIR ] || mkdir -p $DIFF_DIR



SINCE=`date +%Y-%m-%d --date="-2 month"`

git log --parents --no-merges --decorate  --since $SINCE > $LOG_FILE
curl http://gitstat.scmacewill.cn:8081/gitstat/proc-git-log-file?path=$LOG_FILE

if [ -f "$DIFF_CMD_FILE" ]; then
	source $DIFF_CMD_FILE
fi
curl http://gitstat.scmacewill.cn:8081/gitstat/proc-git-diff?path=$LOG_FILE
