import React, { useContext, useState } from 'react';
import { observer } from 'mobx-react-lite';
import {
  Button, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tooltip
} from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';
import CodeIcon from '@material-ui/icons/Code';

import {
  ConfigStoreContext, FileDataStoreContext, UiStoreContext, WebworkerStoreContext
} from 'store/stores';
import OpenDialogContent from './OpenDialogContent';
import * as s from './styles';
import BibEntry from '../../../pages/BibEntry'

const Bibtex = observer(({setBibtexOpen}) => {
  const configStore = useContext(ConfigStoreContext);
  const fileDataStore = useContext(FileDataStoreContext);
  const uiStore = useContext(UiStoreContext);
  const webworkerStore = useContext(WebworkerStoreContext);
  const [isOpen, setIsOpen] = useState(false);

  const showOpenDialog = () => {
    setBibtexOpen(true)
  };

  return (
    <>
      {configStore.uiConfig.open_icon
        && (
          <div
            className={s.openButton}
            onClick={showOpenDialog}
          >
            <Tooltip title="Bibtex">
              <IconButton>
                <CodeIcon />
              </IconButton>
            </Tooltip>
          </div>
        )
      }
    </>
  );
});

export default Bibtex;
