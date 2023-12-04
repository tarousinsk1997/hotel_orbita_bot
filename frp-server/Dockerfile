FROM alpine:3

ENV FRP_VERSION=0.52.3
ENV FRP_URL=https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_amd64.tar.gz

WORKDIR /opt/frp

ADD ${FRP_URL} /opt/frp/

RUN tar xzf /opt/frp/frp_${FRP_VERSION}_linux_amd64.tar.gz

RUN rm -r frp_${FRP_VERSION}_linux_amd64.tar.gz

COPY ./frps.toml /opt/frp/frp_${FRP_VERSION}_linux_amd64/frps.toml

CMD ["/opt/frp/frp_0.52.3_linux_amd64/frps", "-c", "/opt/frp/frp_0.52.3_linux_amd64/frps.toml"]