<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import { Checkbox } from '@/components/ui/checkbox'
import { useToast } from '@/components/ui/toast/use-toast'
import { Toaster } from '@/components/ui/toast'
// @ts-ignore
import TradeResultsTable from '@/components/TradeResultsTable.vue';
import { LineChart } from '@/components/ui/chart-line'

const apiUrl = import.meta.env.VITE_BACKEND_URL;

const { toast } = useToast()

const items = ref([]);
const fetchCheckColumns = async () => {
  try {
    const response = await fetch(`${apiUrl}/get-column-names`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    items.value = data;
  } catch (error) {
    console.error('Error fetching columns:', error);
    toast({
      title: 'Error',
      description: 'Failed to fetch the column names from the server.',
    });
  }
}
onMounted(fetchCheckColumns);

const strats = ref([]);
const fetchSelectItems = async () => {
  try {
    const response = await fetch(`${apiUrl}/get-selection-strats`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    strats.value = data;
  } catch (error) {
    console.error('Error fetching select strats:', error);
    toast({
      title: 'Error',
      description: 'Failed to fetch select strats from the server.',
    });
  }
};
onMounted(fetchSelectItems);

const mls = ref([]);
const fetchSelectModels = async () => {
  try {
    const response = await fetch(`${apiUrl}/get-selection-models`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    mls.value = data;
  } catch (error) {
    console.error('Error fetching select mls:', error);
    toast({
      title: 'Error',
      description: 'Failed to fetch select mls from the server.',
    });
  }
};
onMounted(fetchSelectModels);


// Initialize empty data for charts
const analysisChartData1 = ref([]);
const analysisChartData2 = ref([]);
const tradeResults1 = ref();
const tradeResults2 = ref();
const filename = ref('');

const formSchema = toTypedSchema(z.object({
  file: z.any().optional(),
  rowsNumber: z.string().min(1).max(50),
  strategyType: z.string({
    required_error: 'Please select an strategy to use.',
  }),
  mlType: z.string({
    required_error: 'Please select an machine learning model to use.',
  }),
  columns: z.array(z.string()).refine(value => value.some(item => item), {
    message: 'You have to select at least one item.',
  }),
  filename: z.string().min(1).max(50)
}));

const { handleSubmit: handleFormSubmit } = useForm({
  validationSchema: formSchema,
  initialValues: {
    file: null,
    rowsNumber: '',
    strategyType: '',
    mlType: '',
    columns: [],
    filename: ''
  },
});

const onSubmit = handleFormSubmit(async (values) => {
  try {
    toast({
      title: 'Running backtest and machine learning!',
      description: `Please wait for the data to be returned.`,
    });

    filename.value = values.filename; // Store the filename

    const formData = new FormData();
    formData.append('file', values.file);
    formData.append('rowsNumber', values.rowsNumber);
    formData.append('strategyType', values.strategyType);
    formData.append('mlType', values.mlType);
    formData.append('columns', JSON.stringify(values.columns));
    formData.append('filename', values.filename);

    const response = await fetch(`${apiUrl}/submit-form`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const result = await response.json();

    if (Array.isArray(result.analysisChartData1) && result.analysisChartData1.every(isDictionary)) {
      analysisChartData1.value = result.analysisChartData1;
    } else {
      console.error('Invalid data structure for analysisChartData1');
    }

    if (Array.isArray(result.analysisChartData2) && result.analysisChartData2.every(isDictionary)) {
      analysisChartData2.value = result.analysisChartData2;
    } else {
      console.error('Invalid data structure for analysisChartData2');
    }
    tradeResults1.value = result.tradeResults1;
    tradeResults2.value = result.tradeResults2;

    toast({
      title: 'Form submitted successfully',
      description: `The form was submitted successfully.`,
    });
  } catch (error) {
    console.error('Error:', error);
    if (error instanceof Error) {
      toast({
        title: 'Submission error',
        description: `There was an error submitting the form: ${error.message}`,
      });
    } else {
      toast({
        title: 'Submission error',
        description: 'An unknown error occurred while submitting the form',
      });
    }
  }

  console.log(values);
});

const downloadModel = async () => {
  const downloadFilename = filename.value; // Use the stored filename
  if (downloadFilename) {
    try {
      let formData = new FormData();
      formData.append('filename', downloadFilename);

      let response = await fetch(`${apiUrl}/download`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${downloadFilename}.joblib`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        toast({
          title: 'Download successful',
          description: `The file has been downloaded successfully.`,
        });
      } else {
        console.error('Server error:', response);
        toast({
          title: 'Server error',
          description: 'There was an error with the server response.',
        });
      }
    } catch (error) {
      console.error('Error:', error);
      if (error instanceof Error) {
        toast({
          title: 'Download error',
          description: `There was an error downloading the file: ${error.message}`,
        });
      } else {
        toast({
          title: 'Download error',
          description: 'An unknown error occurred',
        });
      }
    }
  }
};

function isDictionary(value: any): boolean {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

watch(analysisChartData1, (newVal) => {
  console.log('analysisChartData1 changed:', newVal);
});

watch(analysisChartData2, (newVal) => {
  console.log('analysisChartData2 changed:', newVal);
});

watch(tradeResults1, (newVal) => {
  console.log('tradeResults1  changed:', newVal);
});

watch(tradeResults2, (newVal) => {
  console.log('tradeResults2  changed:', newVal);
});
</script>

<template>
  <Toaster />
  <ResizablePanelGroup id="demo-group-1" direction="horizontal" class="w-screen rounded-lg border">
    <ResizablePanel id="demo-panel-1" :default-size="20">
      <ResizablePanelGroup id="demo-group-4" direction="vertical">
        <ResizablePanel id="demo-panel-12" :default-size="20">
          <div class="flex h-full items-center justify-center p-6">
            <Dialog>
              <div>
                <DialogTrigger as-child>
                  <Button variant="outline">
                    Add Params
                  </Button>
                </DialogTrigger>
              </div>
              <DialogContent class="sm:max-w-[425px] grid-rows-[auto_minmax(0,1fr)_auto] p-0 max-h-[90dvh]">
                <DialogHeader class="p-6 pb-0">
                  <DialogTitle>Input</DialogTitle>
                  <DialogDescription>
                    Make changes to your machine learning backtest here. Click submit when you're done.
                  </DialogDescription>
                </DialogHeader>
                <div class="grid gap-4 py-4 overflow-y-auto px-6">
                  <div class="flex flex-col justify-between">
                    <form @submit="onSubmit">
                      <FormField v-slot="{ componentField }" name="file">
                        <FormItem>
                          <div class="mb-4">
                            <FormLabel class="text-base">
                              OHLC File:
                            </FormLabel>
                            <FormDescription>
                              The csv data file that contains Open, High, Low, and Close of each candlestick.
                            </FormDescription>
                            <FormControl>
                              <Input v-bind="componentField" id="file" type="file" />
                            </FormControl>
                          </div>
                        </FormItem>
                      </FormField>
                      <FormField v-slot="{ componentField }" name="rowsNumber">
                        <FormItem>
                          <div class="mb-4">
                            <FormLabel class="text-base">
                              # of Rows:
                            </FormLabel>
                            <FormControl>
                              <Input v-bind="componentField" id="rowsNumber" />
                            </FormControl>
                          </div>
                        </FormItem>
                      </FormField>
                      <FormField v-slot="{ componentField }" name="strategyType">
                        <FormItem>
                          <div class="mb-4">
                            <FormLabel class="text-base">
                              Strategy Type:
                            </FormLabel>
                            <Select v-bind="componentField">
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select a strategy to use." />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectGroup>
                                  <SelectItem v-for="strat in strats" :key="strat.value" :value="strat.value">
                                    {{ strat.label }}
                                  </SelectItem>
                                </SelectGroup>
                              </SelectContent>
                            </Select>
                          </div>
                        </FormItem>
                      </FormField>
                      <FormField v-slot="{ componentField }" name="mlType">
                        <FormItem>
                          <div class="mb-4">
                            <FormLabel class="text-base">
                              Machine Learning Type:
                            </FormLabel>
                            <Select v-bind="componentField">
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select a machine learning model to use." />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectGroup>
                                  <SelectItem v-for="ml in mls" :key="ml.value" :value="ml.value">
                                    {{ ml.label }}
                                  </SelectItem>
                                </SelectGroup>
                              </SelectContent>
                            </Select>
                          </div>
                        </FormItem>
                      </FormField>
                      <FormField name="columns">
                        <FormItem>
                          <div class="mb-4">
                            <FormLabel class="text-base">
                              Column Names:
                            </FormLabel>
                          </div>

                          <FormField v-for="item in items" v-slot="{ value, handleChange }" :key="item.id"
                            type="checkbox" :value="item.id" :unchecked-value="false" name="columns">
                            <FormItem class="flex flex-row items-start space-x-3 space-y-0">
                              <FormControl>
                                <Checkbox :checked="value.includes(item.id)" @update:checked="handleChange" />
                              </FormControl>
                              <FormLabel class="font-normal">
                                {{ item.label }}
                              </FormLabel>
                            </FormItem>
                          </FormField>
                          <FormMessage />
                        </FormItem>
                      </FormField>
                      <FormField v-slot="{ componentField }" name="filename">
                        <FormItem>
                          <div class="mb-4">
                            <FormLabel class="text-base">
                              Model Filename:
                            </FormLabel>
                          </div>
                          <FormControl>
                            <Input id="filename" class="col-span-3" v-bind="componentField" />
                          </FormControl>
                        </FormItem>
                      </FormField>
                      <div class="mt-4">
                        <DialogFooter class="p-6 pt-0">
                          <Button type="submit">
                            Submit
                          </Button>
                        </DialogFooter>
                      </div>
                    </form>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
            <Button @click="downloadModel" class="ml-4">
              Download
            </Button>
          </div>
        </ResizablePanel>

        <ResizableHandle id="demo-handle-9" />
        <ResizablePanel id="demo-panel-13" :default-size="75">
          <div class="flex h-full items-center justify-center p-6">
            <TradeResultsTable :tradeData="tradeResults1" />
          </div>
        </ResizablePanel>

        <ResizableHandle id="demo-handle-10" />
        <ResizablePanel id="demo-panel-14" :default-size="75">
          <div class="flex h-full items-center justify-center p-6">
            <TradeResultsTable :tradeData="tradeResults2" />
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
      <div class="flex h-screen items-center justify-center p-6">
      </div>
    </ResizablePanel>

    <ResizableHandle id="demo-handle-1" />
    <ResizablePanel id="demo-panel-2" :default-size="50">
      <ResizablePanelGroup id="demo-group-2" direction="vertical">
        <ResizablePanel id="demo-panel-3" :default-size="25">
          <div class="flex h-full items-center justify-center p-6">
            <LineChart :data="analysisChartData1" index="time" :categories="['value']" :y-formatter="(tick) => {
      return typeof tick === 'number' ? `$ ${new Intl.NumberFormat('us').format(tick).toString()}` : ''
    }" class="h-full w-full" />
          </div>
        </ResizablePanel>
        <ResizableHandle id="demo-handle-2" />
        <ResizablePanel id="demo-panel-4" :default-size="25">
          <div class="flex h-full items-center justify-center p-6">
            <LineChart :data="analysisChartData2" index="time" :categories="['value']" :y-formatter="(tick) => {
      return typeof tick === 'number' ? `$ ${new Intl.NumberFormat('us').format(tick).toString()}` : ''
    }" class="h-full w-full" />
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </ResizablePanel>
  </ResizablePanelGroup>
</template>

<style scoped></style>
