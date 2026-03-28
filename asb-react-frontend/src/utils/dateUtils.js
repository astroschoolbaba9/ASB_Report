/**
 * Normalize any date string to DD-MM-YYYY format for the backend.
 * Handles:
 *   - YYYY-MM-DD (from HTML date picker)
 *   - DD-MM-YYYY (already correct)
 *   - null/undefined (returns empty string)
 */
export const formatDobForBackend = (dateStr) => {
    if (!dateStr) return '';
    const str = dateStr.trim();

    // Already in DD-MM-YYYY format (day is 1-2 digits, year is 4 digits at end)
    if (/^\d{1,2}-\d{1,2}-\d{4}$/.test(str)) {
        return str;
    }

    // YYYY-MM-DD format (from HTML <input type="date">)
    if (/^\d{4}-\d{1,2}-\d{1,2}$/.test(str)) {
        const [y, m, d] = str.split('-');
        return `${d}-${m}-${y}`;
    }

    // Fallback: return as-is
    return str;
};
