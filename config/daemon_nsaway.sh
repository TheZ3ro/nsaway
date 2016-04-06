#! /bin/sh

NAME=nsaway
DESC="NSAway daemon"
PIDFILE="/var/run/${NAME}.pid"
LOGFILE="/var/log/${NAME}.log"

# Python binary path
DAEMON=`which python`

# Path of your python script
DAEMON_OPTS="/usr/share/nsaway/nsaway.py"

START_OPTS="--start --background --pidfile ${PIDFILE} --exec ${DAEMON} ${DAEMON_OPTS}"
STOP_OPTS="--stop --pidfile ${PIDFILE}"

test -x "${DAEMON}" || exit 0

set -e

case "$1" in
start)
  echo -n "Starting ${DESC}: "
  start-stop-daemon $START_OPTS
  echo "$NAME."
;;
stop)
  echo -n "Stopping $DESC: "
  start-stop-daemon $STOP_OPTS
  echo "$NAME."
  rm -f $PIDFILE
;;
restart|force-reload)
  echo -n "Restarting $DESC: "
  start-stop-daemon $STOP_OPTS
  sleep 1
  start-stop-daemon $START_OPTS
  echo "$NAME."
;;
pid)
  cat $PIDFILE
;;
*)
  N=/etc/init.d/$NAME
  echo "Usage: $N {start|stop|restart|force-reload|pid}" >&2
  exit 1
;;
esac

exit 0
