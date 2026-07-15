/**
 * 成绩管理页面 - 渐变蓝科技风
 */
import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Space, Tag, Modal, Form,
  Select, message, Popconfirm, InputNumber
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { scoreApi, studentApi, courseApi } from '../../api';
import type { Score, Student, Course } from '../../types';

const Scores: React.FC = () => {
  const [data, setData] = useState<Score[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingScore, setEditingScore] = useState<Score | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
    loadOptions();
  }, [pagination.current, pagination.pageSize, searchText]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res: any = await scoreApi.getList({
        page: pagination.current,
        page_size: pagination.pageSize,
        search: searchText,
      });
      setData(res.data.list);
      setPagination(prev => ({ ...prev, total: res.data.total }));
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadOptions = async () => {
    try {
      const [studentRes, courseRes] = await Promise.all([
        studentApi.getList({ page: 1, page_size: 1000 }),
        courseApi.getList({ page: 1, page_size: 1000 }),
      ]);
      setStudents(studentRes.data.list);
      setCourses(courseRes.data.list);
    } catch (error) {
      console.error('加载选项失败', error);
    }
  };

  const handleSearch = (value: string) => {
    setSearchText(value);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingScore(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Score) => {
    setEditingScore(record);
    form.setFieldsValue({
      ...record,
      student_id: record.student_id,
      course_id: record.course_id,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await scoreApi.delete(id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingScore) {
        await scoreApi.update(editingScore.id, values);
        message.success('更新成功');
      } else {
        await scoreApi.create(values);
        message.success('录入成功');
      }
      setModalVisible(false);
      loadData();
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  // 等级颜色映射
  const getGradeStyle = (grade: string) => {
    const styles: Record<string, { bg: string; color: string }> = {
      'A': { bg: 'rgba(0, 229, 255, 0.2)', color: '#00e5ff' },
      'B': { bg: 'rgba(30, 151, 243, 0.2)', color: '#1e97f3' },
      'C': { bg: 'rgba(140, 216, 239, 0.2)', color: '#8cd8ef' },
      'D': { bg: 'rgba(255, 171, 0, 0.2)', color: '#ffab00' },
      'E': { bg: 'rgba(255, 82, 82, 0.2)', color: '#ff5252' },
    };
    return styles[grade] || { bg: 'rgba(107, 114, 128, 0.2)', color: '#9cb3cc' };
  };

  // 卡片样式
  const cardStyle = {
    borderRadius: 12,
    background: 'rgba(10, 22, 40, 0.85)',
    border: '1px solid rgba(30, 58, 95, 0.6)',
    backdropFilter: 'blur(10px)',
  };

  const columns: ColumnsType<Score> = [
    { title: '学号', dataIndex: 'student_no', width: 100 },
    { title: '学生姓名', dataIndex: 'student_name', width: 100 },
    { title: '课程号', dataIndex: 'course_no', width: 100 },
    { title: '课程名称', dataIndex: 'course_name', width: 150 },
    {
      title: '成绩',
      dataIndex: 'score',
      width: 80,
      render: (score) => (
        <span style={{ 
          color: '#f0f4f8', 
          fontWeight: 600,
          textShadow: score >= 60 ? '0 0 8px rgba(0, 229, 255, 0.5)' : '0 0 8px rgba(255, 82, 82, 0.5)',
        }}>
          {score?.toFixed(1) || '-'}
        </span>
      )
    },
    {
      title: '等级',
      dataIndex: 'grade',
      width: 60,
      render: (grade) => grade ? (
        <Tag style={{ 
          background: getGradeStyle(grade).bg,
          border: 'none',
          color: getGradeStyle(grade).color,
        }}>
          {grade}
        </Tag>
      ) : '-'
    },
    { title: '学期', dataIndex: 'semester', width: 100 },
    {
      title: '考试类型',
      dataIndex: 'exam_type',
      width: 80,
      render: (type) => {
        const types: Record<string, string> = {
          'regular': '平时',
          'midterm': '期中',
          'final': '期末',
        };
        return types[type] || type;
      }
    },
    {
      title: '操作',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            style={{ color: '#8cd8ef' }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button 
              type="link" 
              size="small" 
              danger 
              icon={<DeleteOutlined />}
              style={{ color: '#ff5252' }}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    },
  ];

  return (
    <Card style={cardStyle}>
      {/* 搜索和操作栏 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Input.Search
            placeholder="搜索学生姓名、学号、课程名"
            onSearch={handleSearch}
            style={{ width: 260 }}
            allowClear
          />
        </Space>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
          style={{
            borderRadius: 8,
            background: 'linear-gradient(30deg, #1e97f3 0%, #8cd8ef 100%)',
            border: 'none',
            boxShadow: '0 4px 18px rgba(30, 151, 243, 0.45)',
          }}
        >
          录入成绩
        </Button>
      </div>

      {/* 数据表格 */}
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => setPagination(prev => ({ ...prev, current: page, pageSize })),
        }}
        bordered
        size="middle"
        style={{ background: 'transparent' }}
      />

      {/* 新增/编辑弹窗 */}
      <Modal
        title={<span style={{ color: '#f0f4f8' }}>{editingScore ? '编辑成绩' : '录入成绩'}</span>}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={500}
        styles={{
          body: { padding: 24 },
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="student_id"
            label={<span style={{ color: '#9ca3af' }}>学生</span>}
            rules={[{ required: true, message: '请选择学生' }]}
          >
            <Select
              showSearch
              placeholder="请选择学生"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.children as any)?.props?.children?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {students.map(s => (
                <Select.Option key={s.id} value={s.id}>
                  {s.student_no} - {s.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="course_id"
            label={<span style={{ color: '#9ca3af' }}>课程</span>}
            rules={[{ required: true, message: '请选择课程' }]}
          >
            <Select placeholder="请选择课程">
              {courses.map(c => (
                <Select.Option key={c.id} value={c.id}>
                  {c.course_no} - {c.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="score"
              label={<span style={{ color: '#9ca3af' }}>成绩</span>}
              rules={[{ required: true, message: '请输入成绩' }]}
              style={{ flex: 1 }}
            >
              <InputNumber
                min={0}
                max={100}
                precision={1}
                style={{ width: '100%' }}
                placeholder="0-100"
              />
            </Form.Item>
            <Form.Item 
              name="semester" 
              label={<span style={{ color: '#9ca3af' }}>学期</span>} 
              style={{ flex: 1 }}
            >
              <Input placeholder="如: 2024-1" />
            </Form.Item>
          </div>

          <Form.Item 
            name="exam_type" 
            label={<span style={{ color: '#9ca3af' }}>考试类型</span>} 
            initialValue="final"
          >
            <Select>
              <Select.Option value="regular">平时</Select.Option>
              <Select.Option value="midterm">期中</Select.Option>
              <Select.Option value="final">期末</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item 
            name="remarks" 
            label={<span style={{ color: '#9ca3af' }}>备注</span>}
          >
            <Input.TextArea rows={2} placeholder="备注信息（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default Scores;
