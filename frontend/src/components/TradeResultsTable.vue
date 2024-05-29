<template>
    <div class="trade-results-container">
        <p class="trade-result" v-for="(value, key) in tradeData" :key="key">
            <span class="key">{{ formatKey(key) }}:</span>
            <span class="value">{{ value }}</span>
        </p>
    </div>
</template>

<script>
export default {
    props: {
        tradeData: {
            type: Object,
            default: () => ({}),
        },
    },
    methods: {
        formatKey(key) {
            // Converts key from snake_case to Title Case
            return key.replace(/_/g, ' ')
                .toLowerCase()
                .split(' ')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
        },
    },
    mounted() {
        console.log('TradeResultsTable component mounted. tradeData:', this.tradeData);
    },
    watch: {
        tradeData(newVal) {
            console.log('TradeResultsTable component received new tradeData:', newVal);
        }
    }
};
</script>

<style scoped>
.trade-results-container {
    font-size: 12px;
    /* Keeps the font size small for compactness */
    max-width: 100%;
    /* Ensures it doesn't exceed screen width */
    overflow-x: auto;
    /* Allows for horizontal scrolling if necessary */
    color: #0d0c0c;
    /* Sets text color to white */
}

.trade-result {
    margin: 1px 0;
    /* Adds a small vertical space between entries */
    line-height: 1.2;
    /* Slightly increases line height for readability */
}

.key {
    font-weight: bold;
    /* Highlights the key */
}

.value {
    margin-left: 4px;
    /* Adds a small space between key and value for readability */
}
</style>
