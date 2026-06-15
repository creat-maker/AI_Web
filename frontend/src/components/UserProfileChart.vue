<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue';
import { LineChart, RadarChart } from 'echarts/charts';
import { GridComponent, LegendComponent, RadarComponent, TitleComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([TitleComponent, TooltipComponent, LegendComponent, GridComponent, RadarComponent, LineChart, RadarChart, CanvasRenderer]);

const lineEl = ref<HTMLDivElement | null>(null);
const radarEl = ref<HTMLDivElement | null>(null);
const currentUser = ref<any>(null);
const isConnected = ref(false);
let lineChart: echarts.ECharts | null = null;
let radarChart: echarts.ECharts | null = null;
let ws: WebSocket | null = null;
let reconnectTimer: number | null = null;

function renderCharts(data?: any) {
  if (lineEl.value) {
    lineChart = lineChart || echarts.init(lineEl.value);
    lineChart.setOption({
      title: { text: 'User Purchase Trend (Real-time)', left: 'center' },
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'] },
      yAxis: { type: 'value' },
      series: [{ name: 'Purchase Trend', type: 'line', data: data?.purchase_trend || [0, 0, 0, 0, 0, 0], smooth: true }]
    });
  }
  if (radarEl.value) {
    const tagsPool = ['developer', 'gamer', 'reader', 'traveler', 'foodie', 'fitness', 'music'];
    const values = tagsPool.map((tag) => data?.active_tags?.includes(tag) ? 1 : 0);
    radarChart = radarChart || echarts.init(radarEl.value);
    radarChart.setOption({
      title: { text: 'Active Tags Radar', left: 'center' },
      tooltip: { trigger: 'item' },
      radar: { indicator: tagsPool.map((name) => ({ name, max: 1 })) },
      series: [{ name: 'User Tags', type: 'radar', data: [{ value: values, name: 'Current User Tags' }], areaStyle: { color: 'rgba(54, 162, 235, 0.4)' } }]
    });
  }
}

function connectWebSocket() {
  const wsUrl = import.meta.env.DEV ? 'ws://localhost:8000/ws/user-profile' : `ws://${window.location.host}/ws/user-profile`;
  ws = new WebSocket(wsUrl);
  ws.onopen = () => {
    isConnected.value = true;
    if (reconnectTimer) {
      clearInterval(reconnectTimer);
      reconnectTimer = null;
    }
  };
  ws.onmessage = (event) => {
    try {
      currentUser.value = JSON.parse(event.data);
      renderCharts(currentUser.value);
    } catch {
      currentUser.value = null;
    }
  };
  ws.onclose = () => {
    isConnected.value = false;
    if (!reconnectTimer) reconnectTimer = window.setInterval(connectWebSocket, 3000);
  };
  ws.onerror = () => ws?.close();
}

onMounted(async () => {
  await nextTick();
  renderCharts();
  connectWebSocket();
  window.addEventListener('resize', () => {
    lineChart?.resize();
    radarChart?.resize();
  });
});

onUnmounted(() => {
  if (reconnectTimer) clearInterval(reconnectTimer);
  ws?.close();
  lineChart?.dispose();
  radarChart?.dispose();
});
</script>

<template>
  <div class="user-profile-dashboard">
    <div class="status-panel">
      WebSocket Status:
      <span :class="{ 'status-online': isConnected, 'status-offline': !isConnected }">
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
      <div ref="lineEl" class="chart-wrapper"></div>
      <div ref="radarEl" class="chart-wrapper"></div>
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

.status-online {
  color: green;
}

.status-offline {
  color: red;
}

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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
