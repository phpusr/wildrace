wildrace
========

[![Build Status](https://travis-ci.org/phpusr/wildrace.svg?branch=master)](https://travis-ci.org/phpusr/wildrace)
[![codecov](https://codecov.io/gh/phpusr/wildrace/branch/master/graph/badge.svg)](https://codecov.io/gh/phpusr/wildrace)

There is a group at [vk.com](https://vk.com/club101326589). 
In it, participants share the results of their runs, they add up their distance from the previous one, for example: "1000 + 5 = 1005".
The goal of the group is to unite the runners and to run 1,000,000 km together.

Sometimes participants make mistakes during addition, some statistics are also needed. 
In order for the results to be correct, a bot was created that analyzes the participants' messages and writes them a comment on the processing status. 
In addition, once every 1000 km, he publishes statistics.

The bot is written in Django, uses the Django REST Framework for the web interface API, Django Channels sends data via WebSockets to the web interface, Celery to run periodic tasks.

[The web interface](https://wildrace.herokuapp.com/) is written in Vue.js and updates data automatically through WebSockets.

## Doc

- [How to run](docs/how_to_run.md)
- [Get VK access token](docs/get_vk_access_token.md)
- [Environment variables](docs/env.md)

## Used technologies

### Frontend

- [Vue.js](https://vuejs.org/)
- [Vuex](https://vuex.vuejs.org/)
- [Vuetify](https://vuetifyjs.com/)
- [Vue i18n](https://kazupon.github.io/vue-i18n/)
- [Vue Router](https://router.vuejs.org/)
- [Vue Resource](https://github.com/pagekit/vue-resource)
- [Vue Infinite Loading](https://www.npmjs.com/package/vue-infinite-loading)
- [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Sentry](https://sentry.io/)
- [ESLint](https://eslint.org/)

### Backend

- [Django](https://www.djangoproject.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/en/latest/)
- [Celery](http://www.celeryproject.org/)
- [VK API](https://vk-api.readthedocs.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [Flake8](https://flake8.pycqa.org/en/latest/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Sentry](https://sentry.io/)

## Previous versions

### [v2](https://github.com/phpusr-archive/wildrace-v2)

- Vue.js 2.5
- Spring 2.1
- Kotlin 1.3

### [v1](https://github.com/phpusr-archive/wildrace-v1) (Private)

- jQuery 1.11
- React 0.14
- Grails 2.4
