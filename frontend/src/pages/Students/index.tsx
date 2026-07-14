/**
 * 学生管理页面 - 渐变蓝科技风
 */
import React, { useEffect, useState } from 'react';
import {
  Card, Table, Button, Input, Space, Tag, Modal, Form,
  Select, message, Popconfirm
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { studentApi } from '../../api';
import type { Student } from '../../types';

const Students: React.FC = () => {
  const [data, setData] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, [pagination.current, pagination.pageSize, searchText]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res: any = await studentApi.getList({
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

  const handleSearch = (value: string) => {
    setSearchText(value);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingStudent(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Student) => {
    setEditingStudent(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await studentApi.delete(id);
      message.success('删除成功');
      loadData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingStudent) {
        await studentApi.update(editingStudent.id, values);
        message.success('更新成功');
      } else {
        await studentApi.create(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      loadData();
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  const columns: ColumnsType<Student> = [
    { title: '学号', dataIndex: 'student_no', width: 120 },
    { title: '姓名', dataIndex: 'name', width: 100 },
    {
      title: '性别',
      dataIndex: 'gender',
      width: 60,
      render: (gender) => gender === 'male' ? '男' : '女'
    },
    { title: '专业', dataIndex: 'major', width: 150 },
    { title: '班级', dataIndex: 'class_name', width: 120 },
    { title: '手机', dataIndex: 'phone', width: 130 },
    { title: '邮箱', dataIndex: 'email', width: 180 },
    {
      title: '状态',
      dataIndex: 'status',
      width: 80,
      render: (status) => {
        const map = {
          active: { label: '在读', background: 'rgba(0, 255, 128, 0.15)', color: '#69f0ae' },
          inactive: { label: '休学', background: 'rgba(255, 171, 0, 0.15)', color: '#ffd740' },
          graduated: { label: '毕业', background: 'rgba(30, 151, 243, 0.15)', color: '#1e97f3' },
        };
        const item = map[status as keyof typeof map] || map.active;
        return (
          <Tag style={{ background: item.background, border: 'none', color: item.color }}>
            {item.label}
          </Tag>
        );
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

  // 卡片样式
  const cardStyle = {
    borderRadius: 12,
    background: 'rgba(10, 22, 40, 0.85)',
    border: '1px solid rgba(30, 58, 95, 0.6)',
    backdropFilter: 'blur(10px)',
  };

  return (
    <Card style={cardStyle}>
      {/* 搜索和操作栏 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Input.Search
            placeholder="搜索学号、姓名、邮箱"
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
          新增学生
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
        title={<span style={{ color: '#f0f4f8' }}>{editingStudent ? '编辑学生' : '新增学生'}</span>}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
        styles={{
          body: { padding: 24 },
        }}
      >
        <Form form={form} layout="vertical">
          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="student_no"
              label={<span style={{ color: '#9ca3af' }}>学号</span>}
              rules={[{ required: true, message: '请输入学号' }]}
              style={{ flex: 1 }}
            >
              <Input placeholder="请输入学号" />
            </Form.Item>
            <Form.Item
              name="name"
              label={<span style={{ color: '#9ca3af' }}>姓名</span>}
              rules={[{ required: true, message: '请输入姓名' }]}
              style={{ flex: 1 }}
            >
              <Input placeholder="请输入姓名" />
            </Form.Item>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item 
              name="gender" 
              label={<span style={{ color: '#9ca3af' }}>性别</span>} 
              style={{ flex: 1 }}
            >
              <Select placeholder="请选择">
                <Select.Option value="male">男</Select.Option>
                <Select.Option value="female">女</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item 
              name="major" 
              label={<span style={{ color: '#9ca3af' }}>专业</span>} 
              style={{ flex: 1 }}
            >
              <Input placeholder="请输入专业" />
            </Form.Item>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item 
              name="class_name" 
              label={<span style={{ color: '#9ca3af' }}>班级</span>} 
              style={{ flex: 1 }}
            >
              <Input placeholder="请输入班级" />
            </Form.Item>
            <Form.Item 
              name="phone" 
              label={<span style={{ color: '#9ca3af' }}>手机</span>} 
              style={{ flex: 1 }}
            >
              <Input placeholder="请输入手机号" />
            </Form.Item>
          </div>

          <Form.Item 
            name="email" 
            label={<span style={{ color: '#9ca3af' }}>邮箱</span>}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item 
            name="origin_province" 
            label={<span style={{ color: '#9ca3af' }}>生源地</span>}
          >
            <Input placeholder="请输入生源省份" />
          </Form.Item>

          <Form.Item 
            name="status" 
            label={<span style={{ color: '#9ca3af' }}>状态</span>} 
            initialValue="active"
          >
            <Select>
              <Select.Option value="active">在读</Select.Option>
              <Select.Option value="inactive">休学</Select.Option>
              <Select.Option value="graduated">毕业</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default Students;
