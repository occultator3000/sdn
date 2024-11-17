<template>
    <div class="traffic-chart">
      <div ref="chart" style="width: 100%; height: 100%"></div>
    </div>
  </template>
  
  <script>
  import * as echarts from 'echarts'
  
  export default {
    name: 'TrafficChart',
    
    data() {
      return {
        chart: null,
        timer: null
      }
    },
    
    methods: {
      initChart() {
        this.chart = echarts.init(this.$refs.chart)
        this.updateChart([])
      },
      
      async fetchData() {
        try {
          const response = await this.$axios.get('/api/monitor/flow/history')
          this.updateChart(response.data)
        } catch (error) {
          console.error('获取流量数据失败:', error)
        }
      },
      
      updateChart(data) {
        const option = {
          title: {
            text: '网络流量监控'
          },
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: ['字节数', '数据包数', '流表数']
          },
          xAxis: {
            type: 'category',
            data: data.timestamps || []
          },
          yAxis: [
            {
              type: 'value',
              name: '字节数/数据包数'
            },
            {
              type: 'value',
              name: '流表数'
            }
          ],
          series: [
            {
              name: '字节数',
              type: 'line',
              data: data.bytes || []
            },
            {
              name: '数据包数',
              type: 'line',
              data: data.packets || []
            },
            {
              name: '流表数',
              type: 'line',
              yAxisIndex: 1,
              data: data.flows || []
            }
          ]
        }
        
        this.chart?.setOption(option)
      }
    },
    
    mounted() {
      this.initChart()
      this.fetchData()
      this.timer = setInterval(this.fetchData, 5000)
    },
    
    beforeDestroy() {
      if (this.timer) {
        clearInterval(this.timer)
      }
      this.chart?.dispose()
    }
  }
  </script>
  
  <style scoped>
  .traffic-chart {
    width: 100%;
    height: 100%;
    min-height: 400px;
  }
  </style> 