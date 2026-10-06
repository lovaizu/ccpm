const fs = require('fs');
const os = require('os');
const path = require('path');

const CONFIG_PATH = path.join(os.homedir(), '.config', 'taskctl', 'config.json');
const OLD_CONFIG_PATH = path.join(os.homedir(), '.taskctlrc');

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    if (fs.existsSync(OLD_CONFIG_PATH)) {
      throw new Error(
        `The config file has moved. Move the contents of ${OLD_CONFIG_PATH} to ${CONFIG_PATH}.`
      );
    }
    throw new Error(`Config file not found: ${CONFIG_PATH}`);
  }
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  if (!config.server) {
    throw new Error(`No server in ${CONFIG_PATH}`);
  }
  return config;
}

module.exports = { loadConfig, CONFIG_PATH };
