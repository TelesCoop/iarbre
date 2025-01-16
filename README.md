# 🌳 IArbre

Please find a detailled description of the project (in French) on our [webpage](https://iarbre.fr)

## 📁 Project Structure

Here's how the repository is organized:

```
IArbre/
├── back/      # Backend code (Python Django)
├── front/     # Frontend code (Vue.js)
├── deploy/    # Deployment configurations (Ansible)
└── .pre-commit-config.yaml  # Pre-commit hooks configuration
```

### **back/**

This directory contains the backend of IArbre, built using **Django** 🐍. It processes GIS data to compute the indices and run APIs.

### **front/**

The frontend is built with **Vue.js** 🌟. This mostly handles the map.

### **deploy/**

Deployment is handled using **Ansible** 🛠️, making it simple to deploy and manage IArbre on your servers.

### **.pre-commit-config.yaml**

We care about code quality! The `.pre-commit-config.yaml` file ensures all contributors adhere to best practices by running automated checks before committing changes.

## 🛠️ Setting Up Pre-Commit

Follow these steps to set it up:

1. **Install pre-commit**:

   ```bash
   pip install pre-commit
   ```

2. **Install the hooks**:

   ```bash
   pre-commit install
   ```

3. **Run the hooks manually (optional)**:
   ```bash
   pre-commit run --all-files
   ```

That's it! Now every time you commit, pre-commit will automatically check your code. 🧹✨

## 🤝 Contributing

If you have ideas, bug reports, or feature requests, feel free to open an [issue](https://github.com/TelesCoop/iarbre/issues).

You are also welcome to contribute directly with new features:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b my-awesome-feature`
3. **Commit your changes**: `git commit -m "Add awesome feature"`
4. **Push your branch**: `git push origin my-awesome-feature`
5. **Open a Pull Request**
