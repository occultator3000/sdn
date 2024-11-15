from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.cli import CLI
import logging

logger = logging.getLogger(__name__)

class CustomTopo(Topo):
    """自定义拓扑类"""
    def build(self):
        # 创建交换机
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # 创建主机
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # 添加链路
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(s1, s2)
        self.addLink(s2, s3)

class TopologyManager:
    """拓扑管理器"""
    def __init__(self):
        self.net = None
        self.topo = CustomTopo()
        
    async def initialize(self):
        """初始化网络"""
        try:
            self.net = Mininet(
                topo=self.topo,
                controller=RemoteController('c0', ip='127.0.0.1', port=6653)
            )
            self.net.start()
            logger.info("Mininet网络已启动")
        except Exception as e:
            logger.error(f"初始化网络失败: {str(e)}")
            raise

    def get_current_topology(self):
        """获取当前网络拓扑"""
        if not self.net:
            return {"nodes": [], "links": []}
            
        nodes = []
        links = []
        
        # 收集节点信息
        for host in self.net.hosts:
            nodes.append({
                "id": host.name,
                "type": "host",
                "ip": host.IP()
            })
            
        for switch in self.net.switches:
            nodes.append({
                "id": switch.name,
                "type": "switch",
                "dpid": switch.dpid
            })
            
        # 收集链路信息
        for link in self.net.links:
            links.append({
                "source": link.intf1.node.name,
                "target": link.intf2.node.name
            })
            
        return {
            "nodes": nodes,
            "links": links
        }

    def get_statistics(self):
        """获取网络统计信息"""
        if not self.net:
            return {}
            
        stats = {
            "host_count": len(self.net.hosts),
            "switch_count": len(self.net.switches),
            "link_count": len(self.net.links),
            "hosts": {},
            "switches": {}
        }
        
        # 收集主机统计信息
        for host in self.net.hosts:
            stats["hosts"][host.name] = {
                "ip": host.IP(),
                "mac": host.MAC()
            }
            
        # 收集交换机统计信息
        for switch in self.net.switches:
            stats["switches"][switch.name] = {
                "dpid": switch.dpid,
                "ports": len(switch.intfs)
            }
            
        return stats

    async def cleanup(self):
        """清理网络资源"""
        if self.net:
            self.net.stop()
            logger.info("Mininet网络已停止")

if __name__ == '__main__':
    # 创建拓扑
    topo = CustomTopo()
    
    # 创建网络
    net = Mininet(
        topo=topo,
        controller=RemoteController('c0', ip='127.0.0.1', port=6653)
    )
    
    # 启动网络
    net.start()
    
    # 进入CLI
    CLI(net)
    
    # 停止网络
    net.stop() 