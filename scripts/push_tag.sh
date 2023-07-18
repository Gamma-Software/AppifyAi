# Verify we are on main branch
git branch --show-current | grep -q "main"

# If the branch is not main, exit with an error
if [ $? -ne 0 ]; then
    echo "You are not on the main branch"
    exit 1
fi

# Get the version (ex: 1.0.0) in the generative_app/version.py file that has the following format: VERSION="1.0.0"
get_version() {
    version=v$(grep -oP '(?<=VERSION=")[^"]*' generative_app/version.py)
}

# Check if the version is not already tagged
git tag | grep -q $version

# If the version is already tagged, exit with an error
if [ $? -eq 0 ]; then
    echo "Version $version is already tagged"
    exit 1
fi

# Otherwise tag the version
git tag "$version"