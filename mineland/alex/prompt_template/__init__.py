import pkg_resources

def load_prompt(prompt):
    package_path = pkg_resources.resource_filename("alex", "")
    with open(f"{package_path}/prompt_template/{prompt}.txt", "r") as f:
        prompt = f.read()
    return prompt
