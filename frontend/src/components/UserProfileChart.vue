<script setup lang="ts">
import { ref, onMounted, onUnmounted, shallowRef } from 'vue';
import { use } from 'echarts/core';
import { LineChart, RadarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  RadarComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';

// 使用 ECharts 按需引入
use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  RadarComponent,
  LineChart,
  RadarChart,
  CanvasRenderer
]);

const lineChartOption = ref({
  title: {
    text: 'User Purchase Trend (Real-time)',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: 'Purchase Trend',
      type: 'line',
      data: [0, 0, 0, 0, 0, 0],
      smooth: true,
      animationDuration: 1000,
      animationEasing: 'cubicOut'
    }
  ]
});

const radarChartOption = ref({
  title: {
    text: 'Active Tags Radar',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  radar: {
    indicator: [
      { name: 'developer', max: 1 },
      { name: 'gamer', max: 1 },
      { name: 'reader', max: 1 },
      { name: 'traveler', max: 1 },
      { name: 'foodie', max: 1 },
      { name: 'fitness', max: 1 },
      { name: 'music', max: 1 }
    ]
  },
  series: [
    {
      name: 'User Tags',
      type: 'radar',
      data: [
        {
          value: [0, 0, 0, 0, 0, 0, 0],
          name: 'Tags'
        }
      ],
      areaStyle: {
        color: 'rgba(54, 162, 235, 0.4)'
      }
    }
  ]
});

const currentUser = ref<any>(null);
let ws: WebSocket | null = null;
let reconnectTimer: number | null = null;
const isConnected = ref(false);

const connectWebSocket = () => {
  const wsUrl = `ws://${window.location.host}/ws/user-profile`;
  // Fallback for dev mode
  const url = import.meta.env.DEV ? 'ws://localhost:8000/ws/user-profile' : wsUrl;
  
  ws = new WebSocket(url);

  ws.onopen = () => {
    console.log('WebSocket connected');
    isConnected.value = true;
    if (reconnectTimer) {
      clearInterval(reconnectTimer);
      reconnectTimer = null;
    }
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      currentUser.value = data;
      
      // Update line chart reactive option
      lineChartOption.value = {
        ...lineChartOption.value,
        series: [
          {
            ...lineChartOption.value.series[0],
            data: data.purchase_trend
          }
        ]
      };

      // Update radar chart reactive option
      const tagsPool = ['developer', 'gamer', 'reader', 'traveler', 'foodie', 'fitness', 'music'];
      const radarValues = tagsPool.map(tag => data.active_tags.includes(tag) ? 1 : 0);
      
      radarChartOption.value = {
        ...radarChartOption.value,
        series: [
          {
            ...radarChartOption.value.series[0],
            data: [
              {
                value: radarValues,
                name: 'Current User Tags'
              }
            ]
          }
        ]
      };

    } catch (e) {
      console.error('Error parsing WS data', e);
    }
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
    isConnected.value = false;
    // Auto reconnect mechanism
    if (!reconnectTimer) {
      reconnectTimer = window.setInterval(() => {
        console.log('Attempting to reconnect...');
        connectWebSocket();
      }, 3000);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    ws?.close();
  };
};

onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  if (reconnectTimer) {
    clearInterval(reconnectTimer);
  }
  if (ws) {
    ws.close();
  }
});
</script>

<template>
  <div class="user-profile-dashboard">
    <div class="status-panel">
      WebSocket Status: 
      <span :class="{'status-online': isConnected, 'status-offline': !isConnected}">
        {{ isConnected ? 'Connected' : 'Reconnecting...' }}
      </span>
    </div>

    <div v-if="currentUser" class="user-info-cards">
      <div class="card">
        <h3>Current User</h3>
        <p><strong>ID:</strong> {{ currentUser.user_id }}</p>
        <p><strong>Age Group:</strong> {{ currentUser.age_group }}</p>
        <p><strong>Gender:</strong> {{ currentUser.gender }}</p>
        <p><strong>Region:</strong> {{ currentUser.region }}</p>
      </div>
    </div>

    <div class="charts-container">
      <div class="chart-wrapper">
        <v-chart class="chart" :option="lineChartOption" autoresize />
      </div>
      <div class="chart-wrapper">
        <v-chart class="chart" :option="radarChartOption" autoresize />
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-profile-dashboard {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-panel {
  font-weight: bold;
}
.status-online { color: green; }
.status-offline { color: red; }

.user-info-cards {
  display: flex;
  gap: 20px;
}
.card {
  border: 1px solid var(--border-light);
  padding: 15px;
  border-radius: 8px;
  background-color: var(--bg-neutral);
  min-width: 250px;
}
.card h3 {
  margin-top: 0;
}

.charts-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.chart-wrapper {
  flex: 1;
  min-width: 400px;
  height: 400px;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
