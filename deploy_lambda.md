### Deployment to AWS Lambda

```bash
$ poetry shell

# for the first time
$ zappa init

# deploy code to the specific stage
$ zappa deploy dev

# on each code update for the given stage
$ zappa update dev
```

### Troubleshooting

```bash
$ zappa status dev  # status for the specific stage
$ zappa tail dev  # show logs for the specific stage
```
