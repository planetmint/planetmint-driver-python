FROM tarantool/tarantool:2.8.3

ARG branch=main

RUN wget https://raw.githubusercontent.com/planetmint/planetmint/${branch}/planetmint/backend/tarantool/init.lua
RUN mv init.lua /opt/tarantool/init.lua

#RUN addgroup -S nonroot
#RUN adduser -S nonroot -G nonroot
#RUN chown -R nonroot:nonroot /etc/tarantool
#RUN chown -R nonroot:nonroot /var/run/tarantool
#RUN chown -R nonroot:nonroot /var/lib/tarantool
#RUN chown -R nonroot:nonroot /opt/tarantool

#USER nonroot