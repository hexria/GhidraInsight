# Plugin Marketplace

GhidraInsight plugin marketplace allows you to discover, install, and manage community-contributed analysis plugins.

## Overview

The marketplace provides:
- Plugin discovery and search
- One-click installation
- Plugin ratings and reviews
- Community contributions

## Using the Marketplace

### Search Plugins

```python
from ghidrainsight.plugins import PluginMarketplace

marketplace = PluginMarketplace()

# Search for plugins
plugins = marketplace.search("string analysis")

# Get popular plugins
popular = marketplace.get_popular(limit=10)

# Get plugins by tag
crypto_plugins = marketplace.get_by_tag("crypto")
```

### Install Plugin

```python
# Install a plugin
plugin = plugins[0]  # Get from search results
success = marketplace.install(plugin)

if success:
    print(f"Installed {plugin.name} v{plugin.version}")
```

### List Installed Plugins

```python
# List installed plugins
installed = marketplace.list_installed()
for name, info in installed.items():
    print(f"{name}: {info['version']}")
```

### Uninstall Plugin

```python
# Uninstall a plugin
marketplace.uninstall("plugin_name")
```

## Contributing Plugins

### 1. Create Your Plugin

Create a plugin following the [Plugin Development Guide](PLUGIN_DEVELOPMENT.md).

### 2. Publish to GitHub

1. Create a GitHub repository
2. Add topic `ghidrainsight-plugin`
3. Add plugin metadata (optional `plugin.json`)

### 3. Plugin Metadata

Create `plugin.json` in your repository:

```json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Does awesome analysis",
  "tags": ["security", "strings"],
  "entry_point": "plugin.py",
  "requirements": ["requests>=2.0"]
}
```

### 4. Submit to Marketplace

Plugins are automatically discovered when:
- Repository has `ghidrainsight-plugin` topic
- Contains valid plugin file
- Follows naming conventions

## Plugin Tags

Common tags:
- `security` - Security analysis
- `crypto` - Cryptography detection
- `strings` - String analysis
- `entropy` - Entropy analysis
- `malware` - Malware detection
- `network` - Network analysis

## Best Practices

1. **Clear Documentation**: Document what your plugin does
2. **Versioning**: Use semantic versioning
3. **Testing**: Include tests
4. **Examples**: Provide usage examples
5. **Tags**: Use appropriate tags for discoverability

## Community Plugins

Browse community plugins:
- [GitHub Topics](https://github.com/topics/ghidrainsight-plugin)
- Marketplace cache (local)

## Updating Cache

```python
# Update local plugin cache
marketplace.update_cache()
```

---

For plugin development, see [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md).
