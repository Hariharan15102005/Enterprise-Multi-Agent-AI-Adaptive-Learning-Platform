import React, { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { CustomersPage } from './pages/CustomersPage';
import { LogisticsPage } from './pages/LogisticsPage';
import { SellersPage } from './pages/SellersPage';
import { MLIntelligencePage } from './pages/MLIntelligencePage';
import { AIAnalystPage } from './pages/AIAnalystPage';
import { DataQualityPage } from './pages/DataQualityPage';
import { SystemHealthPage } from './pages/SystemHealthPage';

export function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');

  const renderCurrentPage = () => {
    switch (currentTab) {
      case 'dashboard':
        return <DashboardPage onNavigate={setCurrentTab} />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'customers':
        return <CustomersPage />;
      case 'logistics':
        return <LogisticsPage />;
      case 'sellers':
        return <SellersPage />;
      case 'ml':
        return <MLIntelligencePage />;
      case 'ai':
        return <AIAnalystPage />;
      case 'quality':
        return <DataQualityPage />;
      case 'health':
        return <SystemHealthPage />;
      default:
        return <DashboardPage onNavigate={setCurrentTab} />;
    }
  };

  return (
    <Layout currentTab={currentTab} onSelectTab={setCurrentTab}>
      {renderCurrentPage()}
    </Layout>
  );
}

export default App;
