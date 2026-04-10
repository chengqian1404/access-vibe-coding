import React, { useState, useEffect } from 'react';
import {
  Typography, Card, Row, Col, Tag, Button, Input, Empty, Spin, Space, Tooltip,
} from 'antd';
import { SearchOutlined, PlayCircleOutlined, CopyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getBackendUrl } from '../config';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;

const FALLBACK_TEMPLATES = [
  {
    id: '1',
    category: '数据表',
    title: '创建员工信息表',
    description: '创建包含基本字段的员工信息表',
    instruction: '创建一个"员工信息"表，包含员工ID（自动编号）、姓名（文本）、部门（文本）、工资（货币）、入职日期（日期）字段',
    tags: ['建表', '员工'],
  },
  {
    id: '2',
    category: '数据表',
    title: '创建产品库存表',
    description: '创建产品和库存管理表',
    instruction: '创建一个"产品库存"表，包含产品ID（自动编号）、产品名称（文本）、单价（货币）、库存数量（数字）、类别（文本）字段',
    tags: ['建表', '库存'],
  },
  {
    id: '3',
    category: '数据导入',
    title: '从 Excel 导入数据',
    description: '将 Excel 文件中的数据导入到 Access',
    instruction: '从桌面的 data.xlsx 文件导入数据到"销售记录"表，第一行为标题行',
    tags: ['导入', 'Excel'],
  },
  {
    id: '4',
    category: '查询',
    title: '筛选高薪员工',
    description: '查询工资超过指定金额的员工',
    instruction: '创建一个查询，从"员工信息"表中筛选出工资大于8000的员工，显示姓名、部门和工资字段',
    tags: ['查询', '筛选'],
  },
  {
    id: '5',
    category: '窗体',
    title: '创建数据录入窗体',
    description: '为表格创建数据录入界面',
    instruction: '为"员工信息"表创建一个简洁的数据录入窗体，包含所有字段的输入框',
    tags: ['窗体', 'UI'],
  },
  {
    id: '6',
    category: '报表',
    title: '生成部门统计报表',
    description: '按部门统计员工人数和平均工资',
    instruction: '生成一份按部门统计的报表，显示各部门的员工人数和平均工资',
    tags: ['报表', '统计'],
  },
];

function Templates() {
  const [templates, setTemplates] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    if (!searchText) {
      setFiltered(templates);
    } else {
      const q = searchText.toLowerCase();
      setFiltered(templates.filter(t =>
        t.title.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q) ||
        t.instruction.toLowerCase().includes(q) ||
        t.category.toLowerCase().includes(q)
      ));
    }
  }, [searchText, templates]);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const baseUrl = await getBackendUrl();
      const res = await axios.get(`${baseUrl}/api/v1/templates`);
      const data = res.data.templates;
      setTemplates(data.length > 0 ? data : FALLBACK_TEMPLATES);
    } catch {
      setTemplates(FALLBACK_TEMPLATES);
    } finally {
      setLoading(false);
    }
  };

  const handleUse = (template) => {
    navigate('/', { state: { instruction: template.instruction } });
  };

  const handleCopy = (instruction) => {
    navigator.clipboard.writeText(instruction);
  };

  // Group by category
  const categories = [...new Set(filtered.map(t => t.category))];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={4} style={{ margin: 0 }}>📚 指令模板</Title>
        <Search
          placeholder="搜索模板..."
          allowClear
          style={{ width: 250 }}
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
          prefix={<SearchOutlined />}
        />
      </div>

      <Spin spinning={loading}>
        {filtered.length === 0 ? (
          <Empty description="未找到匹配的模板" />
        ) : (
          categories.map(category => (
            <div key={category} style={{ marginBottom: 24 }}>
              <Title level={5} style={{ marginBottom: 12, color: '#1677ff' }}>
                {category}
              </Title>
              <Row gutter={[16, 16]}>
                {filtered.filter(t => t.category === category).map(template => (
                  <Col key={template.id} xs={24} sm={12} lg={8}>
                    <Card
                      className="template-card"
                      hoverable
                      size="small"
                      actions={[
                        <Tooltip title="复制指令" key="copy">
                          <Button type="text" icon={<CopyOutlined />} size="small" onClick={() => handleCopy(template.instruction)}>
                            复制
                          </Button>
                        </Tooltip>,
                        <Tooltip title="使用此模板" key="use">
                          <Button type="text" icon={<PlayCircleOutlined />} size="small" onClick={() => handleUse(template)}>
                            使用
                          </Button>
                        </Tooltip>,
                      ]}
                    >
                      <Card.Meta
                        title={<Text strong style={{ fontSize: 14 }}>{template.title}</Text>}
                        description={
                          <Space direction="vertical" size={4} style={{ width: '100%' }}>
                            <Text type="secondary" style={{ fontSize: 12 }}>{template.description}</Text>
                            <Paragraph
                              ellipsis={{ rows: 2, tooltip: template.instruction }}
                              style={{ margin: 0, fontSize: 12, color: '#595959' }}
                            >
                              {template.instruction}
                            </Paragraph>
                            <Space size={4} wrap>
                              {template.tags?.map(tag => (
                                <Tag key={tag} style={{ fontSize: 11, margin: 0 }}>{tag}</Tag>
                              ))}
                            </Space>
                          </Space>
                        }
                      />
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          ))
        )}
      </Spin>
    </div>
  );
}

export default Templates;
