### Agriculture Management

Agriculture Management System adalah aplikasi terpadu untuk mengelola seluruh aktivitas operasional pertanian secara terstruktur, terukur, dan berbasis data. Aplikasi ini dirancang untuk membantu petani, agribisnis, maupun pengelola lahan dalam meningkatkan produktivitas, efisiensi biaya, serta memastikan kualitas hasil panen.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app agriculture_management
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/agriculture_management
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
