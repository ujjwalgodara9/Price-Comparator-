const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');

const config = getDefaultConfig(__dirname);

// Custom resolver to fix "expo-router/entry-classic could not be found".
// Metro doesn't resolve package subpaths from within node_modules on Windows
// without this explicit intercept.
const originalResolveRequest = config.resolver.resolveRequest;
config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (moduleName === 'expo-router/entry-classic') {
    return {
      filePath: path.resolve(__dirname, 'node_modules/expo-router/entry-classic.js'),
      type: 'sourceFile',
    };
  }
  // Fall through to default resolver
  if (originalResolveRequest) {
    return originalResolveRequest(context, moduleName, platform);
  }
  return context.resolveRequest(context, moduleName, platform);
};

module.exports = config;
