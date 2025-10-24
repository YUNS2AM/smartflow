import { useState, useEffect } from 'react';
import { ArrowLeft, CalendarDays, CheckCircle, Percent, Download, Play } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { scheduleAPI, convertScheduleForGantt, type ScheduleResult } from '../utils/api';
import { Sidebar } from '../components/Sidebar';
import { Calendar, momentLocalizer, View } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import 'moment/locale/ko';

moment.locale('ko');
const localizer = momentLocalizer(moment);

interface SchedulePageProps {
  onNavigate: (page: string) => void;
  onLogout: () => void;
}

interface GanttItem {
  id: string;
  machine: string;
  orderNumber: string;
  productCode: string;
  start: number;
  end: number;
  duration: number;
  color: string;
  isOnTime: boolean;
}

export function SchedulePage({ onNavigate, onLogout }: SchedulePageProps) {
  const [scheduleData, setScheduleData] = useState<ScheduleResult | null>(null);
  const [ganttData, setGanttData] = useState<GanttItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [calendarView, setCalendarView] = useState<View>('week');
  

  const calendarEvents = scheduleData?.schedules.map((schedule) => ({
    title: `${schedule.machine_id}: ${schedule.order_number}`,
    start: new Date(schedule.start_time),
    end: new Date(schedule.end_time),
    resource: {
      machine: schedule.machine_id,
      order: schedule.order_number,
      product: schedule.product_code,
      isOnTime: schedule.is_on_time,
    },
  })) || [];

  // 기존 스케줄 결과 불러오기
  const fetchSchedule = async () => {
    try {
      setIsLoading(true);
      const data = await scheduleAPI.getResult();
      setScheduleData(data);
      
      // 간트차트 데이터 변환
      const gantt = data.schedules.map((schedule, index) => 
        convertScheduleForGantt(schedule, index)
      );
      setGanttData(gantt);
      
      toast.success('스케줄을 불러왔습니다');
    } catch (error: any) {
      console.error('스케줄 조회 실패:', error);
      // 404는 스케줄이 없는 것이므로 에러 메시지 표시 안 함
      if (error.response?.status !== 404) {
        toast.error('스케줄을 불러오는데 실패했습니다');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 새 스케줄 생성
  const handleGenerateSchedule = async () => {
    if (!confirm('새로운 스케줄을 생성하시겠습니까?')) return;

    try {
      setIsGenerating(true);
      toast.info('스케줄 생성 중... (최대 3초 소요)');
      
      const startTime = Date.now();
      const data = await scheduleAPI.generate();
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
      
      setScheduleData(data);
      
      // 간트차트 데이터 변환
      const gantt = data.schedules.map((schedule, index) => 
        convertScheduleForGantt(schedule, index)
      );
      setGanttData(gantt);
      
      toast.success(`스케줄이 생성되었습니다! (${elapsed}초)`, {
        description: `납기 준수율 ${data.metrics.on_time_rate}% | 가동률 ${data.metrics.utilization}%`,
      });
    } catch (error: any) {
      console.error('스케줄 생성 실패:', error);
      toast.error(error.response?.data?.detail || '스케줄 생성에 실패했습니다');
    } finally {
      setIsGenerating(false);
    }
  };

  // 스케줄 엑셀 다운로드
  const handleDownloadSchedule = () => {
    if (!scheduleData) {
      toast.error('다운로드할 스케줄이 없습니다');
      return;
    }
    
    const url = scheduleAPI.downloadExcel();
    window.open(url, '_blank');
    toast.info('스케줄 다운로드를 시작합니다');
  };

  // 컴포넌트 마운트 시 스케줄 불러오기
  useEffect(() => {
    fetchSchedule();
  }, []);

  // 메트릭
  const deliveryRate = scheduleData?.metrics.on_time_rate || 0;
  const utilizationRate = scheduleData?.metrics.utilization || 0;

  return (
  <div className="flex min-h-screen bg-gradient-to-br from-[#F0F9FF] via-[#F9FAFB] to-[#F0FFFE]">
    <Sidebar currentPage="schedule" onNavigate={onNavigate} onLogout={onLogout} />
    
    <div className="flex-1 flex flex-col">
      <header className="bg-white border-b border-[#E5E7EB] sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#2563EB] rounded-lg flex items-center justify-center">
              <CalendarDays className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-[#1F2937] text-2xl">생산 스케줄 결과</h1>
              <p className="text-sm text-[#6B7280]">
                {scheduleData ? 'AI가 생성한 최적 생산 일정입니다' : '스케줄을 생성해주세요'}
              </p>
            </div>
          </div>
          
          <Button
            onClick={handleGenerateSchedule}
            disabled={isGenerating}
            className="bg-[#10B981] hover:bg-[#059669]"
          >
            <Play className="w-4 h-4 mr-2" />
            {isGenerating ? '생성 중...' : '새 스케줄 생성'}
          </Button>
        </div>
      </header>

      <main className="flex-1 p-6">
        {isLoading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#2563EB]"></div>
            <p className="mt-2 text-gray-500">스케줄 불러오는 중...</p>
          </div>
        ) : !scheduleData ? (
          <div className="text-center py-20">
            <CalendarDays className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">스케줄이 없습니다</h3>
            <p className="text-gray-500 mb-6">주문을 등록한 후 스케줄을 생성하세요</p>
            <Button onClick={handleGenerateSchedule} disabled={isGenerating}>
              <Play className="w-4 h-4 mr-2" />
              {isGenerating ? '생성 중...' : '스케줄 생성하기'}
            </Button>
          </div>
        ) : (
          <>
            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Card className={`bg-white ${deliveryRate >= 90 ? 'border-green-200' : 'border-yellow-200'}`}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">납기 준수율</CardTitle>
                  <CheckCircle className={`h-4 w-4 ${deliveryRate >= 90 ? 'text-green-500' : 'text-yellow-500'}`} />
                </CardHeader>
                <CardContent>
                  <div className={`text-4xl font-bold ${deliveryRate >= 90 ? 'text-green-600' : 'text-yellow-600'}`}>
                    {deliveryRate.toFixed(1)}%
                  </div>
                  <p className="text-xs text-gray-500">
                    {scheduleData.metrics.on_time_orders}/{scheduleData.metrics.total_orders} 주문 준수
                  </p>
                </CardContent>
              </Card>
              
              <Card className={`bg-white ${utilizationRate >= 85 ? 'border-blue-200' : 'border-gray-200'}`}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">설비 가동률</CardTitle>
                  <Percent className={`h-4 w-4 ${utilizationRate >= 85 ? 'text-blue-500' : 'text-gray-500'}`} />
                </CardHeader>
                <CardContent>
                  <div className={`text-4xl font-bold ${utilizationRate >= 85 ? 'text-blue-600' : 'text-gray-600'}`}>
                    {utilizationRate.toFixed(1)}%
                  </div>
                  <p className="text-xs text-gray-500">
                    {utilizationRate >= 85 ? '유휴 시간 최소화 달성' : '가동률 개선 필요'}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* 캘린더 뷰 */}
            <Card className="bg-white border border-[#E5E7EB] shadow-lg mb-6 overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-[#E5E7EB]">
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-[#1F2937] flex items-center gap-2">
                      <CalendarDays className="w-5 h-5 text-[#2563EB]" />
                      생산 캘린더
                    </CardTitle>
                    <p className="text-sm text-[#6B7280] mt-1">
                      전체 생산 일정을 한눈에 확인하세요
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant={calendarView === 'week' ? 'default' : 'outline'}
                      onClick={() => setCalendarView('week')}
                      size="sm"
                      className={calendarView === 'week' ? 'bg-[#2563EB] hover:bg-[#1D4ED8]' : ''}
                    >
                      주간
                    </Button>
                    <Button
                      variant={calendarView === 'month' ? 'default' : 'outline'}
                      onClick={() => setCalendarView('month')}
                      size="sm"
                      className={calendarView === 'month' ? 'bg-[#2563EB] hover:bg-[#1D4ED8]' : ''}
                    >
                      월간
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-8">
                <div style={{ height: '800px' }} className="relative bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
                  <Calendar
                    localizer={localizer}
                    events={calendarEvents}
                    startAccessor="start"
                    endAccessor="end"
                    view={calendarView}
                    onView={setCalendarView}
                    views={['week', 'month']}
                    defaultDate={new Date()}
                    messages={{
                      week: '주간',
                      month: '월간',
                      today: '오늘',
                      previous: '이전',
                      next: '다음',
                      showMore: (total) => `+${total} 더보기`,
                    }}
                    eventPropGetter={(event) => {
                      const isOnTime = event.resource.isOnTime;
                      return {
                        className: isOnTime ? 'event-on-time' : 'event-delayed',
                        style: {
                          backgroundColor: isOnTime ? '#10B981' : '#EF4444',
                          borderRadius: '6px',
                          border: 'none',
                        },
                      };
                    }}
                    components={{
                      event: ({ event }) => (
                        <div className="flex flex-col h-full justify-center px-1">
                          <div className="truncate">{event.resource.machine}</div>
                          <div className="truncate text-xs opacity-90">{event.resource.order}</div>
                        </div>
                      ),
                      toolbar: (props) => {
                        const goToBack = () => {
                          props.onNavigate('PREV');
                        };
                        const goToNext = () => {
                          props.onNavigate('NEXT');
                        };
                        const goToToday = () => {
                          props.onNavigate('TODAY');
                        };

                        const label = () => {
                          const date = moment(props.date);
                          return (
                            <span className="rbc-toolbar-label">
                              {props.view === 'month' 
                                ? date.format('YYYY년 M월')
                                : `${date.clone().startOf('week').format('M월 D일')} - ${date.clone().endOf('week').format('M월 D일')}`
                              }
                            </span>
                          );
                        };

                        return (
                          <div className="rbc-toolbar">
                            <div className="rbc-btn-group">
                              <button type="button" onClick={goToToday}>오늘</button>
                              <button type="button" onClick={goToBack}>이전</button>
                              <button type="button" onClick={goToNext}>다음</button>
                            </div>
                            {label()}
                            <div className="flex items-center gap-3">
                              <div className="flex items-center gap-2 text-sm">
                                <div className="w-4 h-4 rounded" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}></div>
                                <span className="text-gray-600">납기 준수</span>
                              </div>
                              <div className="flex items-center gap-2 text-sm">
                                <div className="w-4 h-4 rounded" style={{ background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)' }}></div>
                                <span className="text-gray-600">납기 지연</span>
                              </div>
                            </div>
                          </div>
                        );
                      },
                    }}
                    dayLayoutAlgorithm="no-overlap"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Schedule Visualization */}
            <Card className="bg-white border border-[#E5E7EB] shadow-md">
              <Tabs defaultValue="gantt-chart">
                <CardHeader className="flex flex-row items-center justify-between">
                  <TabsList>
                    <TabsTrigger value="gantt-chart">간트 차트</TabsTrigger>
                    <TabsTrigger value="table-view">상세 테이블</TabsTrigger>
                  </TabsList>
                  <Button variant="outline" onClick={handleDownloadSchedule}>
                    <Download className="w-4 h-4 mr-2" />
                    일정표 다운로드
                  </Button>
                </CardHeader>
                <CardContent>
                  <TabsContent value="gantt-chart" className="pt-4">
                    {ganttData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={ganttData} layout="vertical" barCategoryGap="30%">
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis type="number" unit="h" />
                          <YAxis dataKey="machine" type="category" width={80} />
                          <Tooltip 
                            cursor={{ fill: 'rgba(240, 240, 240, 0.5)' }}
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                const data = payload[0].payload as GanttItem;
                                return (
                                  <div className="bg-white p-3 border rounded shadow-lg">
                                    <p className="font-bold">{data.orderNumber}</p>
                                    <p className="text-sm text-gray-600">{data.productCode}</p>
                                    <p className="text-sm">시작: {data.start}h</p>
                                    <p className="text-sm">종료: {data.end}h</p>
                                    <p className="text-sm">소요: {data.duration}h</p>
                                    <p className={`text-sm font-medium ${data.isOnTime ? 'text-green-600' : 'text-red-600'}`}>
                                      {data.isOnTime ? '✓ 납기 준수' : '✗ 납기 지연'}
                                    </p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Bar dataKey="start" stackId="a" fill="transparent" />
                          <Bar dataKey="duration" stackId="a" name="소요시간">
                            {ganttData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="text-center py-10 text-gray-500">
                        간트차트 데이터가 없습니다
                      </div>
                    )}
                  </TabsContent>
                  
                  <TabsContent value="table-view">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>사출기</TableHead>
                          <TableHead>주문번호</TableHead>
                          <TableHead>제품코드</TableHead>
                          <TableHead>시작 시간</TableHead>
                          <TableHead>종료 시간</TableHead>
                          <TableHead>소요 시간</TableHead>
                          <TableHead>납기 준수</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {scheduleData.schedules.map((item, index) => {
                          const startDate = new Date(item.start_time);
                          const endDate = new Date(item.end_time);
                          
                          return (
                            <TableRow key={`${item.order_number}-${index}`}>
                              <TableCell className="font-medium">{item.machine_id}</TableCell>
                              <TableCell>{item.order_number}</TableCell>
                              <TableCell>{item.product_code}</TableCell>
                              <TableCell>{startDate.toLocaleString('ko-KR')}</TableCell>
                              <TableCell>{endDate.toLocaleString('ko-KR')}</TableCell>
                              <TableCell>{Math.round(item.duration_minutes / 60)}시간</TableCell>
                              <TableCell>
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  item.is_on_time 
                                    ? 'bg-green-100 text-green-700' 
                                    : 'bg-red-100 text-red-700'
                                }`}>
                                  {item.is_on_time ? '✓ 준수' : '✗ 지연'}
                                </span>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TabsContent>
                </CardContent>
              </Tabs>
            </Card>
          </>
        )}
      </main>
    </div>
  </div>
  );
}
