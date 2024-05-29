<script>
import { createChart } from 'lightweight-charts';

// Lightweight Chart instances are stored as normal JS variables
// If you need to use a ref then it is recommended that you use `shallowRef` instead
let series;
let chart;

// Function to get the correct series constructor name for current series type.
function getChartSeriesConstructorName(type) {
  return `add${type.charAt(0).toUpperCase() + type.slice(1)}Series`;
}

// Creates the chart series and sets the data.
const addSeriesAndData = (type, seriesOptions, data) => {
  const seriesConstructor = getChartSeriesConstructorName(type);
  series = chart[seriesConstructor](seriesOptions);
  series.setData(data);
};

const addTradeMarkers = (trades) => {
  const markers = trades.map(trade => {
    const entryMarker = {
      time: trade.entry,
      position: 'belowBar',
      color: '#2196F3',
      shape: 'arrowUp',
      text: 'Entry @ ' + trade.entryPrice.toFixed(2),
    };

    const exitMarker = {
      time: trade.exit,
      position: 'aboveBar',
      color: '#e91e63',
      shape: 'arrowDown',
      text: 'Exit @ ' + trade.exitPrice.toFixed(2),
    };

    return [entryMarker, exitMarker];
  }).flat();

  series.setMarkers(markers);
};

// Auto resizes the chart when the browser window is resized.
const resizeHandler = (container) => {
  if (!chart || !container) return;
  const dimensions = container.getBoundingClientRect();
  chart.resize(dimensions.width, dimensions.height);
};

export default {
  props: {
    type: {
      type: String,
      default: 'line',
    },
    data: {
      type: Object,
      default: () => [],
    },
    autosize: {
      default: true,
      type: Boolean,
    },
    chartOptions: {
      type: Object,
    },
    seriesOptions: {
      type: Object,
    },
    timeScaleOptions: {
      type: Object,
    },
    priceScaleOptions: {
      type: Object,
    },
    trades: {
      type: Object,
      default: () => [],
    }
  },
  mounted() {
    // Create the Lightweight Charts Instance using the container ref.
    chart = createChart(this.$refs.chartContainer, this.chartOptions);
    addSeriesAndData(this.type, this.seriesOptions, this.data);
    addTradeMarkers(this.trades);

    if (this.priceScaleOptions) {
      chart.priceScale().applyOptions(this.priceScaleOptions);
    }

    if (this.timeScaleOptions) {
      chart.timeScale().applyOptions(this.timeScaleOptions);
    }

    chart.timeScale().fitContent();

    if (this.autosize) {
      window.addEventListener('resize', () =>
        resizeHandler(this.$refs.chartContainer)
      );
    }
  },
  unmounted() {
    if (chart) {
      chart.remove();
      chart = null;
    }
    if (series) {
      series = null;
    }
  },
  watch: {
    autosize(enabled) {
      if (!enabled) {
        window.removeEventListener('resize', () =>
          resizeHandler(this.$refs.chartContainer)
        );
        return;
      }
      window.addEventListener('resize', () =>
        resizeHandler(this.$refs.chartContainer)
      );
    },
    type(newType) {
      if (series && chart) {
        chart.removeSeries(series);
      }
      addSeriesAndData(this.type, this.seriesOptions, this.data);
      addTradeMarkers(this.trades);
    },
    data(newData) {
      series.setData(newData);
    },
    trades(newTrades) {
      addTradeMarkers(newTrades);
    },
    chartOptions(newOptions) {
      if (!chart) return;
      chart.applyOptions(newOptions);
    },
    seriesOptions(newOptions) {
      if (!series) return;
      series.applyOptions(newOptions);
    },
    priceScaleOptions(newOptions) {
      if (!chart) return;
      chart.priceScale().applyOptions(newOptions);
    },
    timeScaleOptions(newOptions) {
      if (!chart) return;
      chart.timeScale().applyOptions(newOptions);
    },
  },
  methods: {
    fitContent() {
      if (!chart) return;
      chart.timeScale().fitContent();
    },
    getChart() {
      return chart;
    },
  },
  expose: ['fitContent', 'getChart'],
};
</script>

<template>
  <div class="lw-chart" ref="chartContainer"></div>
</template>

<style scoped>
.lw-chart {
  height: 100%;
}
</style>
