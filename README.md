This is a starting point for Python solutions to the
["Build Your Own Redis" Challenge](https://codecrafters.io/challenges/redis).

In this challenge, you'll build a toy Redis clone that's capable of handling
basic commands like `PING`, `SET` and `GET`. Along the way we'll learn about
event loops, the Redis protocol and more. 

**Note**: If you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to signup for early access.

## Usage

1. Ensure you have `python (3.7)` or higher installed locally
1. Run `./spawn_redis_server.sh` to run the Redis server, which is implemented in
   `app/`.
1. The Redis server will be launched and bound to port `6379`, the default
Redis port. You can speak to it using the redis-cli. You can compile the redis server +
cli directly [from source](https://redis.io/topics/quickstart) or install on macOS via homebrew

```
brew install redis
```

or use your favorite linux package manager. Simply start up the cli by typing
`redis-cli` in the terminal.

## TODO

* Currently querying via telnet doesn't work, as far as I can tell, because
if you try to write a command in accordance with [RESP](https://redis.io/topics/protocol#resp-simple-strings), for exmaple
`set redis awesome`, which is

```*2\r\n$3\r\nset\r\n$5\r\nredis\r\n\$7\r\nawesome\r\n``` 

telnet just escapes all the CRLF `\r\n` and thus the parser doesn't work correctly.
* handling concurrent clients is implemented via threads, whereas real Redis implementation is
single-threaded and based on event-loops. Likewise, key expiry uses a sleeping thread, that only
wakes up after the Time-To-Live (TTL) has passed. There is a more elegant way.
* Implement more data types and commands
