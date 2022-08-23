FROM tarantool/tarantool:2.8.3

ARG branch=main

RUN wget https://raw.githubusercontent.com/planetmint/planetmint/${branch}/planetmint/backend/tarantool/basic.lua
RUN mv basic.lua /opt/tarantool/basic.lua