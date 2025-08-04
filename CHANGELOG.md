# Release notes

<!-- do not remove -->

## 0.3.0

### New Features

- Add Plash Auth ([#54](https://github.com/AnswerDotAI/plash_cli/pull/54)), thanks to [@RensDimmendaal](https://github.com/RensDimmendaal)


## 0.2.2


### Bugs Squashed

- UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 107: character maps to <undefined> ([#56](https://github.com/AnswerDotAI/plash_cli/issues/56))


## 0.2.1

### New Features

- fix wording around plash deploy ([#53](https://github.com/AnswerDotAI/plash_cli/issues/53))

### Bugs Squashed

- Unable to `plash_login` ([#52](https://github.com/AnswerDotAI/plash_cli/issues/52))

- Fix quoting issue ([#51](https://github.com/AnswerDotAI/plash_cli/pull/51)), thanks to [@thomasht86](https://github.com/thomasht86)


## 0.2.0

### New Features

- add force data overwrite flag ([#46](https://github.com/AnswerDotAI/plash_cli/issues/46))



## 0.1.3

### New Features

- create app names that adhere to the 3-4 words naming scheme ([#41](https://github.com/AnswerDotAI/plash_cli/issues/41))


## 0.1.2

### New Features

- feat: add flag to list all user apps ([#36](https://github.com/AnswerDotAI/plash_cli/issues/36))



## 0.1.1

### New Features

- migrate app id to app name ([#35](https://github.com/AnswerDotAI/plash_cli/issues/35))

- have log end when build is done ([#34](https://github.com/AnswerDotAI/plash_cli/issues/34))

### Bugs Squashed

- exception error name incorrect ([#33](https://github.com/AnswerDotAI/plash_cli/issues/33))


## 0.1.0

### New Features

- Streamline using cli with different plash server host names ([#20](https://github.com/AnswerDotAI/plash_cli/issues/20))


## 0.0.5

### New Features

- add flag to specify app id when deploying ([#12](https://github.com/AnswerDotAI/plash_cli/issues/12))

- Option to fetch build or app logs in the CLI ([#8](https://github.com/AnswerDotAI/plash_cli/pull/8)), thanks to [@pydanny](https://github.com/pydanny)
  - This changes the following:

1. Provides a new option for display of logs, specifically the build logs
2. Defaults the log to output build logs, rather than app logs

This change will make it easier to investigate failed deployments and other problems

This change is dependant on a forthcoming change to Plash.

- add ability to deploy a single python script using pep 723 inline dep syntax ([#5](https://github.com/AnswerDotAI/plash_cli/issues/5))



## 0.0.3

### New Features

- add new cli commands for parity with website ([#7](https://github.com/AnswerDotAI/plash_cli/issues/7))
  - resolved in https://github.com/AnswerDotAI/plash_cli/pull/4

- change cli auth to oauth ([#6](https://github.com/AnswerDotAI/plash_cli/issues/6))



## 0.0.2




## 0.0.1



