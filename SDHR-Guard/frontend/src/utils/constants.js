export const CONTROLLER_STATUS = {
  RUNNING: 'running',
  STOPPED: 'stopped',
  ERROR: 'error'
}

export const ALERT_TYPES = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  SUCCESS: 'success'
}

export const REFRESH_INTERVALS = {
  CONTROLLERS: 30000, // 30秒
  TOPOLOGY: 60000,    // 1分钟
  TRAFFIC: 5000       // 5秒
} 