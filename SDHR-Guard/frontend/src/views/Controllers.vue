<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            控制器管理
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              @click="refreshControllers"
              :loading="loading"
            >
              刷新
              <v-icon right>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>

          <v-card-text>
            <controller-list />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ControllerList from '@/components/Controllers/ControllerList.vue'

export default {
  name: 'Controllers',
  
  components: {
    ControllerList
  },

  data: () => ({
    loading: false
  }),

  methods: {
    async refreshControllers() {
      this.loading = true
      try {
        await this.$store.dispatch('controllers/fetchControllers')
      } finally {
        this.loading = false
      }
    }
  }
}
</script> 