# Financial Services Example Bot

This is an example chatbot demonstrating how to build AI assistants for financial services and banking. This starter pack can be used as a base for your own development or as a reference guide for implementing common banking-industry features with Rasa. It includes pre-built intents, actions, and stories for handling conversation flows like checking spending history and transferring money to another account.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Financial Services Example Bot](#financial-services-example-bot)
  - [Install dependencies](#install-dependencies)
  - [Run the bot](#run-the-bot)
  - [Overview of the files](#overview-of-the-files)
  - [Things you can ask the bot](#things-you-can-ask-the-bot)
  - [Testing the bot](#testing-the-bot)
  - [Rasa X Deployment](#rasa-x-deployment)
  - [Action Server Image](#action-server-image)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Install dependencies

Run:
```bash
pip install -r requirements.txt
```

To install development dependencies:

```bash
pip install -r requirements-dev.txt
pre-commit install
python -m spacy download en_core_web_md en
python -m spacy link en_core_web_md en
```

> With pre-commit installed, the `black` and `doctoc` hooks will run on every `git commit`.
> If any changes are made by the hooks, you will need to re-add changed files and re-commit your changes.

## Run the bot

Use `rasa train` to train a model.

Then, to run, first set up your action server in one terminal window, listening on port 5056:
```bash
rasa run actions --port 5056
```
 avoid a conflict when you also run the helpdesk bot as described below in the `handoff` section.

In another window, run the duckling server (for entity extraction):

```bash
docker run -p 8000:8000 rasa/duckling
```

Then to talk to the bot, run:
```
rasa shell --debug
```

Note that `--debug` mode will produce a lot of output meant to help you understand how the bot is working
under the hood. To simply talk to the bot, you can remove this flag.


You can also try out your bot locally using Rasa X by running
```
rasa x
```

Refer to our guided workflow in the [Wiki page](https://github.com/RasaHQ/financial-demo/wiki/Using-Rasa-X-with-the-Financial-Demo) for how to get started with Rasa X in local mode.


## Overview of the files

`data/core.md` - contains stories

`data/nlu.md` - contains NLU training data

`actions.py` - contains custom action/api code

`domain.yml` - the domain file, including bot response templates

`config.yml` - training configurations for the NLU pipeline and policy ensemble

`tests/e2e.md` - end-to-end test stories


## Things you can ask the bot

The bot currently has five skills. You can ask it to:
1. Transfer money to another person
2. Check your earning or spending history (with a specific vendor or overall)
3. Answer a question about transfer charges
4. Pay a credit card bill
5. Tell you your account balance

It also has a limited ability to switch skills mid-transaction and then return to the transaction at hand.

For the purposes of illustration, the bot recognises the following fictional credit card accounts:

- `silver`
- `gold`

It recognises the following payment amounts (besides actual currency amounts):

- `minimum balance`
- `current balance`

It recognises the following vendors (for spending history):

- `Starbucks`
- `Amazon`
- `Rewe`

You can change any of these by modifying `actions.py` and the corresponding NLU data.

If configured, the bot can also hand off to another bot in response to the user asking for handoff. More [details on handoff](#handoff) below.

## Testing the bot

You can test the bot on the test conversations by running  `rasa test`.
This will run [end-to-end testing](https://rasa.com/docs/rasa/user-guide/testing-your-assistant/#end-to-end-testing) on the conversations in `tests/conversation_tests.md`.

Note that if duckling is running when you do this, you'll probably see some "failures" because of entities; that's ok! Since duckling entity extraction is not influenced by NLU training data, and since the values of `time` entities depend on when the tests are being run, these have been left unannotated in the conversation tests.

## Rasa X Deployment

To [deploy financial-demo](https://rasa.com/docs/rasa/user-guide/how-to-deploy/), it is highly recommended to make use of the
[one line deploy script](https://rasa.com/docs/rasa-x/installation-and-setup/one-line-deploy-script/) for Rasa X. As part of the deployment, you'll need to set up [git integration](https://rasa.com/docs/rasa-x/installation-and-setup/integrated-version-control/#connect-your-rasa-x-server-to-a-git-repository) to pull in your data and
configurations, and build or pull an action server image.


## Action Server Image

You will need to have docker installed in order to build the action server image. If you haven't made any changes to the action code, you can also use
the [public image on Dockerhub](https://hub.docker.com/r/rasa/financial-demo) instead of building it yourself.


See the Dockerfile for what is included in the action server image,

To build the image:

```bash
docker build . -t <name of your custom image>:<tag of your custom image>
```

To test the container locally, you can then run the action server container with:

```bash
docker run -p 5055:5055 <name of your custom image>:<tag of your custom image>
```

Once you have confirmed that the container works as it should, you can push the container image to a registry with `docker push`

It is recommended to use an [automated CI/CD process](https://rasa.com/docs/rasa/user-guide/setting-up-ci-cd) to keep your action server up to date in a production environment.
