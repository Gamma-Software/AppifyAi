git clone git@github.com:chroma-core/chroma.git --depth 1 chroma
docker build chroma -t chroma-server-image:latest
rm -rf chroma