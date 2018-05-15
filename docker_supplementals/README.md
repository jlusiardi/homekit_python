# Regression tests with docker

This test will work on master branch of repository.

## Build docker image

Execute within working copy:

```
docker build -t homekit_python .
```

## Run tests

Execute within working copy:

```
./docker_supplementals/test.sh ${MAILADDRESS}
```
