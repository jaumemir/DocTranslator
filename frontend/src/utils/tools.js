export function formatTime(isoTimeString) {
  // Create a Date object
  const date = new Date(isoTimeString);

  // Get year, month, day, hour, minute, and second
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');

  // Return formatted time string
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}
// Format date
/**
 * Convert ISO time string to YYYY-MM-DD HH:MM:SS format
 * @param {string} isoString - ISO format time string
 * @returns {string} Formatted time string (YYYY-MM-DD HH:MM:SS)
 */
export function formatDate(isoString) {
  // 1. Create Date object

  const date = new Date(isoString);

  // 2. Validate if input is a valid date
  if (isNaN(date.getTime())) {
    throw new Error('Invalid ISO date string');
  }

  // 3. Get time components
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  // 4. Concatenate to target format
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

