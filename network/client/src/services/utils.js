export function updateObject(left, right) {
    for (const [key, value] of Object.entries(right)) {
        left[key] = value;
    }
}
