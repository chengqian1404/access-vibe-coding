import React, { useState } from 'react';
import { Input, Button, Space, Tooltip, Typography } from 'antd';
import { SendOutlined, ClearOutlined, BulbOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Text } = Typography;

const EXAMPLE_INSTRUCTIONS = [
  '创建一个"员工信息"表，包含员工ID、姓名、部门、工资、入职日期字段',
  '从 C:\\data\\sales.xlsx 导入销售数据到"销售记录"表',
  '创建一个查询，筛选出工资大于8000的员工',
  '为"员工信息"表创建一个数据录入窗体',
  '生成一份按部门统计工资总额的报表',
];

function InstructionInput({ onSubmit, loading = false }) {
  const [instruction, setInstruction] = useState('');
  const [showExamples, setShowExamples] = useState(false);

  const handleSubmit = () => {
    const trimmed = instruction.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit();
    }
  };

  const handleExample = (example) => {
    setInstruction(example);
    setShowExamples(false);
  };

  return (
    <div className="instruction-input">
      <div className="instruction-header">
        <Text strong style={{ fontSize: 16 }}>📝 输入您的指令</Text>
        <Tooltip title="查看示例指令">
          <Button
            type="text"
            icon={<BulbOutlined />}
            onClick={() => setShowExamples(!showExamples)}
            size="small"
          >
            示例
          </Button>
        </Tooltip>
      </div>

      {showExamples && (
        <div className="examples-panel">
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
            点击示例快速填充：
          </Text>
          {EXAMPLE_INSTRUCTIONS.map((ex, i) => (
            <div
              key={i}
              className="example-item"
              onClick={() => handleExample(ex)}
            >
              <Text style={{ fontSize: 13, cursor: 'pointer', color: '#1677ff' }}>
                • {ex}
              </Text>
            </div>
          ))}
        </div>
      )}

      <TextArea
        value={instruction}
        onChange={(e) => setInstruction(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="请描述您想在 Microsoft Access 中执行的操作，例如：&#10;创建一个员工信息表，包含姓名、工资、部门字段..."
        autoSize={{ minRows: 4, maxRows: 8 }}
        disabled={loading}
        style={{ marginTop: 8, fontSize: 14 }}
      />

      <div className="instruction-actions">
        <Text type="secondary" style={{ fontSize: 12 }}>
          Ctrl+Enter 快速提交
        </Text>
        <Space>
          <Button
            icon={<ClearOutlined />}
            onClick={() => setInstruction('')}
            disabled={loading || !instruction}
          >
            清空
          </Button>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSubmit}
            loading={loading}
            disabled={!instruction.trim()}
          >
            执行指令
          </Button>
        </Space>
      </div>
    </div>
  );
}

export default InstructionInput;
