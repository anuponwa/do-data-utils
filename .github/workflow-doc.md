# Github actions to replace manual publish

## Concept

To build this package and publish to PyPI, the steps are as follows:

1. Install twine in the system
```bash
pip install twine
```

2. Build the setup
```bash
python setup.py sdist bdist_wheel
```
This will get you all the distributed package in `dist/` folder.

3. Publish to PyPI

You have to have API token in your `$HOME` folder or `env`
If done it manually, you have to have this `.pyirc` in your `$HOME` directory
```
[pypi]
  username = __token__
  password = <some TOKEN>
```
Then you can run the upload command from `twine`.
```bash
twine upload dist/*
```

## Github actions

Above steps are replicated in the workflow.
You can view the instruction in the [yaml](https://github.com/anuponwa/do-data-utils/blob/main/.github/workflows/python-publish-tag-do-data-utils.yml) file.

### Workflow & Trigger

We always pull from the `main` branch first to ensure we have the latest changes.

```bash
git checkout main
git pull origin main
```

Then we create a new release branch from main.

```bash
git checkout -b release/x.y.z main
```


For example, we are in `release/x.y.z` branch and we've finished our work.
We push to the repo.

```bash
git commit -m "Done with this release"
git push origin release/x.y.z
```

### Continuous tests

The continuous testing workflow (Github actions) will run and check for static type hints and unittests.

The tests will run with every push to `release/*` branches and every pull request to the `main` branch.


### Automate publish to PyPI

We then create tag and push the tag

The workflow (that builds and publishes to PyPI) is triggered *only* when a new tag is pushed to the repo.

```bash
git tag x.y.z
git push origin x.y.z
```