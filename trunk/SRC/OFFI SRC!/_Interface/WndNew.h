
#ifndef __WNDNEW__H
#define __WNDNEW__H
#include "WndField.h"

class CWndNew : public CWndNeuz 
{ 
public: 
	CWndNew(); 
	~CWndNew(); 

	CWndInventory* m_pInventory;
	CItemBase*	m_pUpgradeItem;
	CWndStatic*		m_pStatic;

	virtual BOOL Initialize( CWndBase* pWndParent = NULL, DWORD nType = MB_OK ); 
	virtual BOOL OnChildNotify( UINT message, UINT nID, LRESULT* pLResult ); 
	virtual void OnDraw( C2DRender* p2DRender ); 
	virtual	void OnInitialUpdate(); 
	virtual BOOL OnCommand( UINT nID, DWORD dwMessage, CWndBase* pWndBase ); 
	virtual void OnSize( UINT nType, int cx, int cy ); 
	virtual void OnLButtonUp( UINT nFlags, CPoint point ); 
	virtual void OnLButtonDown( UINT nFlags, CPoint point ); 
	void SetItem(CItemBase*	m_pItem);
}; 
#endif
